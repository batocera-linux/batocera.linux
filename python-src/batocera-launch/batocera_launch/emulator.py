from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import field
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Final, Self

from batocera_common.paths import SAVES
from batocera_launch.dataclasses import cached_dataclass
from batocera_launch.devices.controller import generate_sdl_game_controller_config
from batocera_launch.fs import mount_overlayfs, mount_squashfs
from batocera_launch.functools import cached_property

if TYPE_CHECKING:
    from argparse import Namespace
    from collections.abc import AsyncGenerator, Container

    from batocera_launch.command import Command
    from batocera_launch.config.config import Config, SystemConfig
    from batocera_launch.devices.controller import Controllers
    from batocera_launch.devices.device import DeviceInfoMapping
    from batocera_launch.devices.gun import Guns
    from batocera_launch.types import HotkeysContext, Resolution


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
    metadata: dict[str, str]
    controllers: Controllers
    guns: Guns
    wheels: DeviceInfoMapping
    resolution: Resolution

    _prepared_rom: Path | None = field(init=False, default=None)

    @property
    def rom(self) -> Path:
        return self.config.rom

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
    @abstractmethod
    def hotkeygen_context(self) -> HotkeysContext: ...

    @property
    def execution_path(self) -> Path | None:
        return None

    @property
    def saves_path(self) -> Path:
        return SAVES / self.system

    @property
    def video_mode(self) -> str:
        return self.config.video_mode

    @property
    def needs_mouse(self) -> bool:
        return False

    @property
    def needs_bezels(self) -> bool:
        return True

    @property
    def needs_overlayfs(self) -> bool:
        return False

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
        match self.config.get_str('controllers.guns.borderscolor', 'white').lower():
            case 'red':
                return '#ff0000'
            case 'green':
                return '#00ff00'
            case 'blue':
                return '#0000ff'
            case _:
                return '#ffffff'

    async def prepare_hud(self, command: Command, /) -> None:
        hud_bezel = await self.prepare_hud_bezel()
        if self.config.get('hud', 'none') != 'none' or hud_bezel is not None:
            command.update_env(
                MANGOHUD_DLSYM='1',
                MANGOHUD_CONFIGFILE=self.prepare_hud_config(),
            )

            if self.needs_bezels:
                command.prepend_args('mangohud')

    async def prepare_hud_bezel(self) -> Path | None:
        # TODO
        return None

    def prepare_hud_config(self) -> Path:
        return Path('/var/run/hud.config')

    def prepare_gun_help(self) -> None:
        # TODO
        return None

    def draw_gun_borders(self) -> None:
        if not self.needs_bezels or self.config.get_bool('hud_support'):
            _logger.debug('skipping drawing gun borders for emulator %s', self.config.emulator)
            return

        gun_borders_size = self.guns_borders_size
        if gun_borders_size is not None:
            _logger.debug('using gun borders for emulator %s', self.name)

            try:
                from .draw.gun_borders import draw_gun_borders

                draw_gun_borders(gun_borders_size, self.gun_borders_color, self.guns_border_ratio)
            except Exception:
                _logger.exception('Failed to draw_gun_borders for gun_borders')

    @asynccontextmanager
    async def prepare_rom(emulator: Emulator, /) -> AsyncGenerator[Path]:
        if emulator.rom.suffix != '.squashfs':
            yield emulator.rom
            return

        async with mount_squashfs(emulator.rom) as squashfs_rom:
            if not emulator.needs_overlayfs:
                yield squashfs_rom
            else:
                async with mount_overlayfs(
                    squashfs_rom, SAVES / emulator.rom.parent.name / emulator.rom.stem
                ) as overlayfs_rom:
                    yield overlayfs_rom

    @abstractmethod
    def configure(self, prepared_rom: Path, /) -> Command: ...

    @asynccontextmanager
    async def get_command(self) -> AsyncGenerator[Command]:
        async with self.prepare_rom() as prepared_rom:
            if execution_path := self.execution_path:
                os.chdir(execution_path)

            if self.needs_sdl_controller_db:
                self.write_sdl_controller_db()

            command = self.configure(prepared_rom)

            if self.needs_sdl_game_controller_config:
                command.update_env(SDL_GAMECONTROLLERCONFIG=self.get_sdl_game_controller_config())

            if self.config.get_bool('hud_support'):
                await self.prepare_hud(command)

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

    @classmethod
    def create(
        cls,
        args: Namespace,
        system_config: SystemConfig,
        metadata: dict[str, str],
        controllers: Controllers,
        guns: Guns,
        wheels: DeviceInfoMapping,
        resolution: Resolution,
        /,
    ) -> Self:
        return cls(
            args.system,
            args.systemname,
            system_config,
            metadata,
            controllers,
            guns,
            wheels,
            resolution,
        )
