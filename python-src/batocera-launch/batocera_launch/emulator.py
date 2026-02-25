from __future__ import annotations

import asyncio
import logging
import tomllib
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from contextlib import AbstractContextManager, asynccontextmanager, chdir, nullcontext
from dataclasses import field
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Final, Self, cast

from batocera_common.asyncio import group_tasks, parallel
from batocera_common.math import clamp
from batocera_common.paths import CONFIGS, ROMS, SAVES

from .config.config import SystemConfig
from .config.metadata import get_games_meta_data
from .dataclasses import cached_dataclass
from .devices.controller import Controller, generate_sdl_game_controller_config
from .devices.gun import Gun, guns_need_crosses
from .devices.video import prepare_resolution
from .devices.wheels import configure_wheels
from .draw.bezel import bezel_overlay
from .draw.gun_borders import create_gun_border_image
from .draw.gun_help import generate_gun_help
from .draw.pil import (
    add_qr_code,
    add_tattoo_image,
    create_transparent_image,
    get_image_size,
    resize_image,
)
from .functools import cached_property
from .paths import ES_GAMES_METADATA, ES_GUNS_ART_METADATA, SYSTEM_DECORATIONS, USER_DECORATIONS
from .rom import Rom
from .types import BezelFiles, BezelInfo

if TYPE_CHECKING:
    from argparse import Namespace
    from collections.abc import AsyncGenerator, Container, Iterator, Mapping

    from .command import Command
    from .config.config import Config
    from .config.es_settings import ESSettings
    from .devices.controller import Controllers
    from .devices.device import DeviceInfoMapping
    from .devices.gun import Guns
    from .types import HotkeysContext, Resolution


_logger: Final = logging.getLogger(__name__)


@cached_dataclass
class Emulator(ABC):
    needs_sdl_game_controller_config: ClassVar[bool] = False
    needs_sdl_controller_db: ClassVar[bool] = False
    sdl_controller_db_path: ClassVar[Path] = Path('/tmp/gamecontrollerdb.txt')
    sdl_game_controller_config_ignore_buttons: ClassVar[Container[str] | None] = None

    system: str
    fancy_system_name: str | None
    config: SystemConfig
    game_info_path: Path

    # These are set after __init__ and __post_init__ in _prepare_devices_and_data
    rom: Rom = field(init=False, default=cast('Rom', None))
    metadata: dict[str, str] = field(init=False, default=cast('dict[str, str]', None))
    controllers: Controllers = field(init=False, default=cast('Controllers', None))
    guns: Guns = field(init=False, default=cast('Guns', None))
    wheels: DeviceInfoMapping = field(init=False, default=cast('DeviceInfoMapping', None))
    resolution: Resolution = field(init=False, default=cast('Resolution', None))

    @property
    def name(self) -> str:
        return self.config.emulator

    @property
    def raw_core(self) -> str | None:
        return self.config.raw_core

    @property
    def core(self) -> str:
        return self.config.core

    @property
    def render_config(self) -> Config:
        return self.config.render_config

    @property
    def es_settings(self) -> ESSettings:
        return self.config.es_settings

    @cached_property
    @abstractmethod
    def hotkeygen_context(self) -> HotkeysContext: ...

    @property
    def execution_path(self) -> Path | None:
        return None

    @cached_property
    def roms_dir(self) -> Path:
        return ROMS / self.system

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / self.name

    @cached_property
    def saves_dir(self) -> Path:
        return SAVES / self.system

    @property
    def video_mode(self) -> str:
        return self.config.video_mode

    @property
    def needs_mouse(self) -> bool:
        return False

    @property
    def handles_bezels(self) -> bool:
        return False

    @property
    def handles_hud(self) -> bool:
        return False

    @property
    def needs_overlayfs(self) -> bool:
        return False

    @cached_property
    def in_game_ratio(self) -> float:
        return 4 / 3

    @cached_property
    def guns_borders_size(self) -> str | None:
        borders_size: str = self.config.get('controllers.guns.borderssize', 'medium')

        # overridden by specific options
        borders_mode = 'normal'
        if (config_borders_mode := (self.config.get('controllers.guns.bordersmode') or 'auto')) != 'auto':
            borders_mode = config_borders_mode
        if (config_borders_mode := (self.config.get('bordersmode') or 'auto')) != 'auto':
            borders_mode = config_borders_mode

        # others are gameonly and normal
        if borders_mode == 'hidden':
            return None

        if borders_mode == 'force':
            return borders_size

        for gun in self.guns:
            if gun.needs_borders:
                return borders_size

        return None

    @cached_property
    def guns_border_ratio(self) -> str | None:
        return self.config.get('controllers.guns.bordersratio', None)

    @cached_property
    def gun_borders_color(self) -> str:
        return self.config.get_str('controllers.guns.borderscolor', 'white').lower()

    @cached_property
    def guns_art_metadata(self) -> Mapping[str, str]:
        if ES_GUNS_ART_METADATA.exists():
            return self.get_games_metadata(ES_GUNS_ART_METADATA)

        _logger.info('metadata file not found : %s', ES_GUNS_ART_METADATA)
        return {}

    @property
    def guns_need_crosses(self) -> bool:
        return guns_need_crosses(self.guns)

    @cached_property
    def game_info(self) -> Mapping[str, str]:
        values: dict[str, str] = {}

        try:
            tree = ET.parse(self.game_info_path)
            root = tree.getroot()
            for child in root:
                for metadata in child:
                    values[metadata.tag] = metadata.text or ''
        except Exception:
            _logger.debug('An error occurred while reading ES metadata')

        return values

    @cached_property
    def decoration_id(self) -> str:
        return 'standalone'

    @cached_property
    def bezel_files(self) -> BezelFiles | None:
        # by order choose :
        # rom name in the system subfolder of the user directory (gb/mario.png)
        # rom name in the system subfolder of the system directory (gb/mario.png)
        # rom name in the user directory (mario.png)
        # rom name in the system directory (mario.png)
        # system name with special graphic in the user directory (gb-90.png)
        # system name in the user directory (gb.png)
        # system name with special graphic in the system directory (gb-90.png)
        # system name in the system directory (gb.png)
        # default name (default.png)
        # else return
        # mamezip files are for MAME-specific advanced artwork (bezels with overlays and backdrops, animated LEDs, etc)

        bezel = self.config.get_str('bezel', 'none')

        if not bezel or bezel == 'none':
            return None

        game_id = self.rom.id

        def candidates() -> Iterator[tuple[Path, bool]]:
            for root in (USER_DECORATIONS, SYSTEM_DECORATIONS):
                yield root / bezel / 'games' / self.system / f'{game_id}.png', True
            for root in (USER_DECORATIONS, SYSTEM_DECORATIONS):
                yield root / bezel / 'games' / f'{game_id}.png', True
            for root in (USER_DECORATIONS, SYSTEM_DECORATIONS):
                if self.decoration_id != '0':
                    yield root / bezel / 'systems' / f'{self.system}-{self.decoration_id}.png', False
                yield root / bezel / 'systems' / f'{self.system}.png', False
            for root in (USER_DECORATIONS, SYSTEM_DECORATIONS):
                yield root / bezel / f'default-{self.decoration_id}.png', True
                yield root / bezel / 'default.png', True

        for png, bezel_game in candidates():
            if png.exists():
                _logger.debug('Original bezel file used: %s', png)
                return BezelFiles(
                    png,
                    png.with_suffix('.info'),
                    png.with_suffix('.lay'),
                    png.with_suffix('.zip'),
                    bezel_game,
                )

        return None

    def get_games_metadata(self, metadata_file: Path) -> dict[str, str]:
        return get_games_meta_data(metadata_file, self.system, self.rom)

    async def prepare_bezel(self) -> Path | None:
        if self.handles_bezels:
            _logger.debug('skipping bezels for emulator %s', self.name)
            return None

        bezel = self.config.get_str('bezel', 'none')
        bezel_tattoo = self.config.get_str('bezel.tattoo', '0')
        bezel_qrcode = self.config.get_str('bezel.qrcode', '0')
        gun_borders_size = self.guns_borders_size

        if (
            (not bezel or bezel == 'none')
            and (not bezel_tattoo or bezel_tattoo == '0')
            and (not bezel_qrcode or bezel_qrcode == '0')
            and gun_borders_size is None
        ):
            return None

        if not bezel or bezel == 'none':
            # no bezel, generate a transparent one for the tatoo/gun borders ... and so on
            overlay_png_path = Path('/tmp/bezel_transhud_black.png')
            overlay_info_path = Path('/tmp/bezel_transhud_black.info')

            create_transparent_image(overlay_png_path, self.resolution.width, self.resolution.height)
            overlay_info_path.write_text(
                f'{{ "width":{self.resolution.width}, "height":{self.resolution.height}, "opacity":1.0000000, "messagex":0.220000, "messagey":0.120000 }}'
            )
        else:
            _logger.debug('hud enabled. trying to apply the bezel %s', bezel)
            if self.bezel_files is None:
                _logger.debug('no bezel info file found')
                return None

            overlay_png_path = self.bezel_files.png
            overlay_info_path = self.bezel_files.info

        bezel_info = BezelInfo.load_from_json(overlay_info_path)
        bezel_width = bezel_info.width
        bezel_height = bezel_info.height

        if bezel_width is None or bezel_height is None:
            bezel_width, bezel_height = get_image_size(overlay_png_path)
            _logger.info('bezel size read from %s', overlay_png_path)

        # max cover proportion and ratio distortion
        max_cover = 0.05  # 5%
        max_ratio_delta = 0.01

        screen_ratio = self.resolution.width / self.resolution.height
        bezel_ratio = bezel_width / bezel_height

        if self.guns_borders_size is None:
            # the screen and bezel ratio must be approximatly the same
            if abs(screen_ratio - bezel_ratio) > max_ratio_delta:
                _logger.debug(
                    'screen ratio (%(screen_ratio)s) is too far from the bezel one (%(bezel_ratio)s) : %(screen_ratio)s - %(bezel_ratio)s > %(max_ratio_delta)s',
                    {'screen_ratio': screen_ratio, 'bezel_ratio': bezel_ratio, 'max_ratio_delta': max_ratio_delta},
                )
                return None

            # the ingame image and the bezel free space must feet
            ## the bezel top and bottom cover must be minimum
            # in case there is a border, force it
            if bezel_info.top is not None and bezel_info.top / bezel_height > max_cover:
                _logger.debug(
                    'bezel top covers too much the game image : %s / %s > %s', bezel_info.top, bezel_height, max_cover
                )
                return None
            if bezel_info.bottom is not None and bezel_info.bottom / bezel_height > max_cover:
                _logger.debug(
                    'bezel bottom covers too much the game image : %s / %s > %s',
                    bezel_info.bottom,
                    bezel_height,
                    max_cover,
                )
                return None

        # if there is no information about top/bottom, assume default is 0

        ## the bezel left and right cover must be maximum
        in_game_ratio = self.in_game_ratio
        img_height = bezel_height
        img_width = img_height * in_game_ratio

        if bezel_info.left is None:
            _logger.debug('bezel has no left info in %s', overlay_info_path)
            # assume default is 4/3 over 16/9
            infos_left = (bezel_width - (bezel_height / 3 * 4)) / 2
            if (
                self.guns_borders_size is None
                and abs((infos_left - ((bezel_width - img_width) / 2.0)) / img_width) > max_cover
            ):
                _logger.debug(
                    'bezel left covers too much the game image : %s / %s > %s',
                    infos_left - ((bezel_width - img_width) / 2.0),
                    img_width,
                    max_cover,
                )
                return None

        if bezel_info.right is None:
            _logger.debug('bezel has no right info in %s', overlay_info_path)
            # assume default is 4/3 over 16/9
            infos_right = (bezel_width - (bezel_height / 3 * 4)) / 2
            if (
                self.guns_borders_size is None
                and abs((infos_right - ((bezel_width - img_width) / 2.0)) / img_width) > max_cover
            ):
                _logger.debug(
                    'bezel right covers too much the game image : %s / %s > %s',
                    infos_right - ((bezel_width - img_width) / 2.0),
                    img_width,
                    max_cover,
                )
                return None

        if self.guns_borders_size is None:
            if (
                bezel_info.left is not None
                and abs((bezel_info.left - ((bezel_width - img_width) / 2.0)) / img_width) > max_cover
            ):
                _logger.debug(
                    'bezel left covers too much the game image : %s / %s > %s',
                    bezel_info.left - ((bezel_width - img_width) / 2.0),
                    img_width,
                    max_cover,
                )
                return None

            if (
                bezel_info.right is not None
                and abs((bezel_info.right - ((bezel_width - img_width) / 2.0)) / img_width) > max_cover
            ):
                _logger.debug(
                    'bezel right covers too much the game image : %s / %s > %s',
                    bezel_info.right - ((bezel_width - img_width) / 2.0),
                    img_width,
                    max_cover,
                )
                return None

        # if screen and bezel sizes doesn't match, resize
        # stretch option
        bezel_stretch = self.config.get_bool('bezel_stretch')
        if bezel_width != self.resolution.width or bezel_height != self.resolution.height:
            _logger.debug('bezel needs to be resized')
            output_png_file = Path('/tmp/bezel.png')
            try:
                resize_image(
                    overlay_png_path,
                    output_png_file,
                    self.resolution.width,
                    self.resolution.height,
                    stretch=bezel_stretch,
                )
            except Exception as e:
                _logger.error('failed to resize the image %s', e)
                return None
            overlay_png_path = output_png_file

        if bezel_tattoo != '0':
            output_png_file = Path('/tmp/bezel_tattooed.png')
            add_tattoo_image(overlay_png_path, output_png_file, self.config)
            overlay_png_path = output_png_file

        if bezel_qrcode != '0' and (cheevos_id := self.game_info.get('cheevosId', '0')) != '0':
            output_png_file = Path('/tmp/bezel_qrcode.png')
            add_qr_code(overlay_png_path, output_png_file, cheevos_id, bezel_qrcode)
            overlay_png_path = output_png_file

        # borders
        if gun_borders_size is not None:
            _logger.debug('Draw gun borders')
            output_png_file = Path('/tmp/bezel_gunborders.png')
            _logger.debug('Gun border ratio = %s', self.guns_border_ratio)
            create_gun_border_image(
                overlay_png_path,
                output_png_file,
                gun_borders_size,
                self.guns_border_ratio,
                inner_color=self.gun_borders_color,
            )
            overlay_png_path = output_png_file

        _logger.debug('applying bezel %s', overlay_png_path)
        return overlay_png_path

    def prepare_hud_config(self, bezel: Path | None, /) -> Path:
        config_lines: list[str] = []

        if (mode := self.config.get('hud', 'none')) == 'none':
            config_lines.append('background_alpha=0')  # hide the background
        else:
            hud_position = 'bottom-left'
            if (hud_corner := self.config.get('hud_corner', '')) != '':
                if hud_corner == 'NW':
                    hud_position = 'top-left'
                elif hud_corner == 'NE':
                    hud_position = 'top-right'
                elif hud_corner == 'SE':
                    hud_position = 'bottom-right'

            # Font Scaling Calculations
            screen_height = self.resolution.height
            font_size = clamp(int(24 * (screen_height / 1080)), 12, 48)

            config_lines.extend(
                [
                    f'font_size={font_size}',
                    f'font_size_text={font_size}',
                    f'position={hud_position}',
                ]
            )

            # Bezel Offset Calculation
            if (self.config.get_str('bezel') or 'none') != 'none' and (
                (bezel is not None and bezel.exists()) or self.handles_bezels
            ):
                offset_x = 0
                active_game_width = int(screen_height * self.in_game_ratio)
                pillar_width = (self.resolution.width - active_game_width) // 2

                if pillar_width > 0:
                    # Push HUD inwards to clear the bezel column
                    if 'left' in hud_position:
                        offset_x = pillar_width + 10  # 10px extra margin inside the game window
                    elif 'right' in hud_position:
                        offset_x = -(pillar_width + 10)

                if offset_x != 0:
                    config_lines.append(f'offset_x={offset_x}')

            # predefined values
            if mode == 'perf':
                config_lines.extend(
                    [
                        'background_alpha=0.9',
                        'legacy_layout=false',
                        'custom_text=%GAMENAME%',
                        'custom_text=%SYSTEMNAME%',
                        'custom_text=%EMULATORCORE%',
                        'fps',
                        'gpu_name',
                        'engine_version',
                        'vulkan_driver',
                        'resolution',
                        'ram',
                        'gpu_stats',
                        'gpu_temp',
                        'cpu_stats',
                        'cpu_temp',
                        'core_load',
                    ]
                )
            elif mode == 'game':
                game_mode_font_size = clamp(int(32 * (screen_height / 1080)), 14, 64)

                config_lines.extend(
                    [
                        'background_alpha=0',
                        'legacy_layout=false',
                        f'font_size={game_mode_font_size}',
                        'image_max_width=200',
                        'image=%THUMBNAIL%',
                        'custom_text=%GAMENAME%',
                        'custom_text=%SYSTEMNAME%',
                        'custom_text=%EMULATORCORE%',
                    ]
                )
            elif mode == 'custom' and (hud_custom := self.config.get_str('hud_custom')):
                config_lines.extend(hud_custom.replace(r'\n', '\n').splitlines())
            else:
                config_lines.append('background_alpha=0')  # hide the background

        emulator = self.name
        if emulator != self.core and self.core:
            emulator = f'{emulator}/{self.core}'

        game_name = self.game_info.get('name', '')
        game_thumbnail = self.game_info.get('thumbnail', '')

        config_path = Path('/var/run/hud.config')
        config_path.write_text(
            ('\n'.join(config_lines) + '\n')
            .replace('%SYSTEMNAME%', self.fancy_system_name or '')
            .replace('%GAMENAME%', game_name or '')
            .replace('%EMULATORCORE%', emulator or '')
            .replace('%THUMBNAIL%', game_thumbnail or '')
        )

        return config_path

    async def prepare_hud(self, command: Command, bezel: Path | None, /) -> None:
        command.update_env(
            MANGOHUD_DLSYM='1',
            MANGOHUD_CONFIGFILE=self.prepare_hud_config(bezel),
        )

        if not self.handles_hud:
            command.prepend_args('mangohud')

    def prepare_gun_help(self) -> None:
        try:
            generate_gun_help(
                self.config.use_guns,
                self.guns,
                self.guns_art_metadata,
                self.resolution,
            )
        except Exception:
            _logger.exception('Failed to generate the gun help image')

    def draw_gun_borders(self) -> None:
        if self.handles_bezels or self.config.get_bool('hud_support'):
            _logger.debug('skipping drawing gun borders for emulator %s', self.config.emulator)
            return

        gun_borders_size = self.guns_borders_size
        if gun_borders_size is not None:
            _logger.debug('using gun borders for emulator %s', self.name)

            try:
                from .draw.gun_borders import draw_gun_borders

                draw_gun_borders(gun_borders_size, self.gun_borders_color, self.guns_border_ratio)
            except Exception:
                _logger.exception('Failed to draw gun borders')

    def prepare_execution_path(self) -> AbstractContextManager[None]:
        if execution_path := self.execution_path:
            return chdir(execution_path)

        return nullcontext()

    @abstractmethod
    async def configure(self) -> Command: ...

    @asynccontextmanager
    async def get_command(self) -> AsyncGenerator[Command]:
        with self.prepare_execution_path():
            if self.needs_sdl_controller_db:
                self.write_sdl_controller_db()

            command = await self.configure()

            if self.needs_sdl_game_controller_config:
                command.update_env(SDL_GAMECONTROLLERCONFIG=self.get_sdl_game_controller_config())

            bezel = await self.prepare_bezel()

            if self.config.get_bool('hud_support') and self.config.get('hud', 'none') != 'none':
                await self.prepare_hud(command, bezel)

            async with bezel_overlay(bezel, self.resolution):
                self.prepare_gun_help()

                if self.config.use_guns and self.guns:
                    self.draw_gun_borders()

                yield command

    def get_sdl_game_controller_config(self) -> str:
        return generate_sdl_game_controller_config(
            self.controllers, ignore_buttons=self.sdl_game_controller_config_ignore_buttons
        )

    def write_sdl_controller_db(self) -> None:
        self.sdl_controller_db_path.write_text(self.get_sdl_game_controller_config())

    @asynccontextmanager
    async def _prepare_devices_and_data(self, args: Namespace, max_players: int, /) -> AsyncGenerator[Self]:
        original_rom = self.config.rom

        async with Rom.prepare(
            original_rom,
            writable_dir=(SAVES / self.config.system / original_rom.stem) if self.needs_overlayfs else None,
        ) as rom:
            self.rom = rom

            controllers, guns, metadata = await group_tasks(
                asyncio.to_thread(Controller.load_for_players, max_players, args),
                asyncio.to_thread(Gun.get_and_precalibrate_all, self.config),
                asyncio.to_thread(self.get_games_metadata, ES_GAMES_METADATA),
            )

            async with parallel(
                configure_wheels(self.config, controllers, metadata), prepare_resolution(self.video_mode)
            ) as ((controllers, wheels), resolution):
                self.controllers = controllers
                self.guns = guns
                self.metadata = metadata
                self.wheels = wheels
                self.resolution = resolution

                self.saves_dir.mkdir(parents=True, exist_ok=True)

                yield self

    @classmethod
    @asynccontextmanager
    async def prepare_emulator(cls, args: Namespace, max_players: int, /) -> AsyncGenerator[Self]:
        emulator = cls(args.system, args.systemname, SystemConfig.load(args), args.gameinfoxml)

        async with emulator._prepare_devices_and_data(args, max_players) as emulator:
            yield emulator


class SpecialDecorationsMixin(Emulator):
    @cached_property
    def decoration_id(self) -> str:
        from importlib import resources

        system_toml = resources.files().joinpath('data', 'special', f'{self.system}.toml')
        if system_toml.is_file():
            special_dict = tomllib.loads(system_toml.read_text())

            rom_compare = self.rom.id.casefold()
            return next((value for key, value in special_dict.items() if rom_compare == key.casefold()), '0')

        return '0'
