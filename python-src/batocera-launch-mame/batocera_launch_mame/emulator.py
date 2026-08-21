from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import Final

from PIL import Image

from batocera_common.paths import BATOCERA_SHARE_DIR, BIOS, CONFIGS, ROMS, SAVES, SCREENSHOTS
from batocera_launch import (
    BezelFiles,
    Command,
    Controller,
    Emulator,
    HotkeysContext,
    SpecialDecorationsMixin,
    cached_dataclass,
    cached_property,
)
from batocera_launch.devices.video import get_screen_info
from batocera_launch.draw.gun_borders import create_gun_border_image
from batocera_launch.draw.pil import create_transparent_image, get_image_size
from batocera_launch.paths import USER_DECORATIONS
from batocera_launch_mame_common import (
    ControlConfig,
    MameControlScheme,
    MessSystemInfo,
    PadConfigMixin,
    get_autorun_command,
    get_input_definition,
    get_machine_size,
    has_stick,
    load_all_mame_control_mappings,
    load_mame_control_scheme,
    reverse_mapping,
    write_pad_config,
)
from batocera_launch_mame_common.paths import (
    MAME_BIN_DIR,
    MAME_BIOS,
    MAME_CHEATS,
    MAME_CONFIG,
    MAME_ROMS,
    MAME_SAVES,
)

_logger: Final = logging.getLogger(__name__)

_SOFT_DIR: Final = Path('/var/run/mame_software')
_HASH_DIR: Final = _SOFT_DIR / 'hash'
_SUBDIR_SOFT_LIST: Final = ['mac_hdd', 'bbc_hdd', 'cdi', 'archimedes_hdd', 'fmtowns_cd']

_PEDAL_KEYS: Final = {1: 'c', 2: 'v', 3: 'b', 4: 'n'}


@cached_dataclass
class MAME(PadConfigMixin, SpecialDecorationsMixin, Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'mame',
            'keys': {
                'exit': 'KEY_ESC',
                'menu': 'KEY_TAB',
                'pause': 'KEY_F5',
                'reset': 'KEY_F3',
                'coin': 'KEY_5',
                'fastforward': 'KEY_PAGEDOWN',
                'save_state': ['KEY_LEFTSHIFT', 'KEY_F6'],
                'restore_state': ['KEY_LEFTSHIFT', 'KEY_F7'],
            },
        }

    @property
    def handles_bezels(self) -> bool:
        return True

    @property
    def execution_path(self) -> Path | None:
        # Change directory to MAME folder (allows data plugin to load properly)
        return MAME_BIN_DIR

    @cached_property
    def mess_system_info(self) -> MessSystemInfo | None:
        return MessSystemInfo.load(self.system)

    @cached_property
    def bezel_set(self) -> str | None:
        bezel_set = self.config.get_str('bezel') or None

        if self.config.get_bool('forceNoBezel'):
            bezel_set = None

        return bezel_set

    @cached_property
    def mame_control_scheme(self) -> MameControlScheme:
        return load_mame_control_scheme(self.config.get_str('altlayout', 'auto'), self.rom.id)

    @cached_property
    def use_mouse(self) -> bool:
        mess_system = self.mess_system_info
        return self.config.get_bool('use_mouse') or not (mess_system is None or not mess_system.name)

    @cached_property
    def all_mame_control_mappings(self) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
        return load_all_mame_control_mappings(self.mame_control_scheme, self.config.use_guns, self.use_mouse)

    async def configure(self) -> Command:
        for path in [
            MAME_CONFIG,
            MAME_SAVES / 'nvram',
            MAME_SAVES / 'cfg',
            MAME_SAVES / 'input',
            MAME_SAVES / 'state',
            MAME_SAVES / 'diff',
            MAME_SAVES / 'comments',
            MAME_BIOS / 'artwork' / 'crosshairs',
            MAME_CHEATS,
            MAME_SAVES / 'plugins',
            MAME_CONFIG / 'ctrlr',
            MAME_CONFIG / 'ini',
        ]:
            path.mkdir(parents=True, exist_ok=True)

        mess_system = self.mess_system_info
        mess_model = '' if mess_system is None else mess_system.name

        soft_list = self.config.get_str('softList', 'none')
        soft_list = soft_list if soft_list != 'none' else ''

        # Auto softlist for FM Towns if there is a zip that matches the folder name
        # Used for games that require a CD and floppy to both be inserted
        if self.system == 'fmtowns' and not soft_list and (ROMS / 'fmtowns' / f'{self.rom.parent.name}.zip').exists():
            soft_list = 'fmtowns_cd'

        args: list[str | Path] = [MAME_BIN_DIR / 'mame', '-sound', 'pipewire', '-skip_gameinfo']

        if mess_system is None:
            args.extend(['-rompath', f'{self.rom.parent};{MAME_BIOS};{BIOS}'])
        else:
            if soft_list in _SUBDIR_SOFT_LIST:
                args.extend(['-rompath', f'{self.rom.parent};{MAME_BIOS};{BIOS};{MAME_ROMS};{_SOFT_DIR}'])
            else:
                args.extend(['-rompath', f'{self.rom.parent};{MAME_BIOS};{BIOS};{MAME_ROMS}'])

        # Various paths
        args.extend(
            [
                '-bgfx_path',
                MAME_BIN_DIR / 'bgfx',
                '-fontpath',
                MAME_BIN_DIR,
                '-languagepath',
                MAME_BIN_DIR / 'language',
                '-pluginspath',
                f'{MAME_BIN_DIR / "plugins"};{MAME_SAVES / "plugins"}',
                '-samplepath',
                MAME_BIOS / 'samples',
                '-artpath',
                f'/var/run/mame_artwork/;{MAME_BIN_DIR / "artwork"};{MAME_BIOS / "artwork"};{USER_DECORATIONS}',
                # Enable cheats
                '-cheat',
                '-cheatpath',
                MAME_CHEATS,
                # Logs and Swithres ini read by default (including its own verbose)
                '-verbose',
                '-switchres_ini',
                # MAME saves a lot of stuff, we need to map this on /userdata/saves/mame/<subfolder> for each one
                '-nvram_directory',
                MAME_SAVES / 'nvram',
            ]
        )

        # Set custom config path if option is selected or default path if not
        custom_cfg = self.config.get_bool('customcfg')

        config_path = (MAME_CONFIG / mess_system.name) if mess_system is not None else MAME_CONFIG
        config_path = (config_path / 'custom') if custom_cfg else config_path

        config_path.mkdir(parents=True, exist_ok=True)

        # MAME will create custom configs per game for MAME ROMs and MESS ROMs with no system attached (LCD games, TV games, etc.)
        # This will allow an alternate config path per game for MESS console/computer ROMs that may need additional config.
        if self.config.get_bool('pergamecfg') and mess_system is not None and mess_system.name:
            config_path = MAME_CONFIG / mess_system.name / self.rom.name
            config_path.mkdir(parents=True, exist_ok=True)

        args.extend(
            [
                '-cfg_directory',
                config_path,
                '-input_directory',
                MAME_SAVES / 'input',
                '-state_directory',
                MAME_SAVES / 'state',
                '-snapshot_directory',
                SCREENSHOTS,
                '-diff_directory',
                MAME_SAVES / 'diff',
                '-comment_directory',
                MAME_SAVES / 'comments',
                '-homepath',
                MAME_SAVES / 'plugins',
                '-ctrlrpath',
                MAME_CONFIG / 'ctrlr',
                '-inipath',
                f'{MAME_CONFIG};{MAME_CONFIG / "ini"}',
                '-crosshairpath',
                MAME_BIOS / 'artwork' / 'crosshairs',
            ]
        )

        if soft_list:
            args.extend(
                [
                    '-swpath',
                    _SOFT_DIR,
                    '-hashpath',
                    _HASH_DIR,
                ]
            )

        # TODO These paths are not handled yet
        # TODO -swpath              path to loose software - might use if we want software list MESS support

        # BGFX video engine : https://docs.mamedev.org/advanced/bgfx.html
        video = self.config.get('video')
        if video == 'bgfx':
            # BGFX backend
            bgfxbackend = self.config.get('bgfxbackend', 'automatic')

            args.extend(
                [
                    '-video',
                    'bgfx',
                    '-bgfx_backend',
                    'auto' if bgfxbackend == 'automatic' else bgfxbackend,
                    # BGFX shaders effects
                    '-bgfx_screen_chains',
                    self.config.get('bgfxshaders', 'default'),
                ]
            )
        # Other video modes
        elif video == 'accel':
            args.extend(['-video', 'accel'])
        else:
            args.extend(['-video', 'auto'])

        # CRT / SwitchRes support
        if self.config.get_bool('switchres'):
            args.extend(['-modeline_generation', '-changeres', '-modesetting', '-readconfig'])
        else:
            args.extend(['-resolution', f'{self.resolution.width}x{self.resolution.height}'])

        # Refresh rate options to help with screen tearing
        # syncrefresh is unlisted, it requires specific display timings and 99.9% of users will get unplayable games.
        # Leaving it so it can be set manually, for CRT or other arcade-specific display users.
        if self.config.get_bool('vsync'):
            args.append('-waitvsync')
        if self.config.get_bool('syncrefresh'):
            args.append('-syncrefresh')

        # Rotation / TATE options
        if (rotation := self.config.get('rotation')) in ['autoror', 'autorol']:
            args.append(f'-{rotation}')

        # Artwork crop
        if self.config.get_bool('artworkcrop'):
            args.append('-artwork_crop')

        # UI enable - for computer systems, the default sends all keys to the emulated system.
        # This will enable hotkeys, but some keys may pass through to MAME and not be usable in the emulated system.
        # Hotkey + D-Pad Up will toggle this when in use (scroll lock key)
        if self.config.get_bool('enableui', True):
            args.append('-ui_active')

        # Load selected plugins
        plugins_to_load: list[str] = []

        if self.config.get_bool('hiscoreplugin', True):
            plugins_to_load.append('hiscore')

        if self.config.get_bool('coindropplugin'):
            plugins_to_load.append('coindrop')

        if self.config.get_bool('dataplugin'):
            plugins_to_load.append('data')

        if self.config.get_bool('offscreenreload'):  # new offscreenreload for light guns games
            plugins_to_load.append('offscreenreload')

        if plugins_to_load:
            args.extend(['-plugins', '-plugin', ','.join(plugins_to_load)])

        use_mouse = self.use_mouse
        device_string = 'mouse' if use_mouse else 'joystick'

        args.extend(
            [
                '-dial_device',
                device_string,
                '-trackball_device',
                device_string,
                '-paddle_device',
                device_string,
                '-positional_device',
                device_string,
                '-mouse_device',
                device_string,
            ]
        )

        if use_mouse:
            args.append('-ui_mouse')

        use_guns = self.config.use_guns
        if not use_guns:
            args.extend(
                [
                    '-lightgun_device',
                    device_string,
                    '-adstick_device',
                    device_string,
                ]
            )

        # Multimouse option currently hidden in ES, SDL only detects one mouse.
        # Leaving code intact for testing & possible ManyMouse integration
        multi_mouse = self.config.get_bool('multimouse')
        if multi_mouse:
            args.append('-multimouse')

        # guns
        if use_guns:
            args.extend(['-lightgunprovider', 'udev', '-lightgun_device', 'lightgun', '-adstick_device', 'lightgun'])

        # wheels
        if self.config.get_bool('multiscreens'):
            screens = await get_screen_info(self.config)
            if len(screens) > 1:
                args.extend(['-numscreens', str(len(screens))])

        special_controller = 'none'

        # Finally we pass game name
        # MESS will use the full filename and pass the system & rom type parameters if needed.
        if not mess_system or not mess_system.name:
            args.append(self.rom.name)
        else:
            # Alternate system for machines that have different configs (ie computers with different hardware)
            if alt_model := self.config.get('altmodel'):
                mess_model = alt_model

            args.append(mess_model)

            system_args, special_controller = self.__get_system_args(mess_system, mess_model, soft_list)
            args.extend(system_args)

            autorun_command, autorun_delay = get_autorun_command(
                self.system, self.rom, mess_system, self.config.get_str('altromtype'), soft_list
            )
            if autorun_command:
                if autorun_command.startswith("'"):
                    autorun_command = autorun_command.replace("'", '')

                args.extend(['-autoboot_delay', str(autorun_delay), '-autoboot_command', autorun_command])

        write_pad_config(self, config_path, mess_model, special_controller)

        # If user provided a custom cmd file at the default location, use that as the customized commandArray
        if (default_custom_cmd_filepath := Path(f'{self.rom}.cmd')).is_file():
            args = default_custom_cmd_filepath.read_text().splitlines()  # pyright: ignore[reportAssignmentType]

        return Command(args, {'PWD': MAME_BIN_DIR, 'XDG_CONFIG_HOME': CONFIGS, 'XDG_CACHE_HOME': SAVES})

    async def prepare_bezel(self) -> Path | None:
        try:
            await self.__write_bezel_config(self.bezel_set)
        except Exception:
            await self.__write_bezel_config(None)

    async def __write_bezel_config(self, bezel_set: str | None, /) -> None:
        mess_system_name = self.mess_system_info.name if self.mess_system_info else None

        tmp_zip_dir = Path('/var/run/mame_artwork') / (mess_system_name if mess_system_name else self.rom.id)

        # clean, in case no bezel is set, and in case we want to recreate it
        if tmp_zip_dir.exists():
            shutil.rmtree(tmp_zip_dir)

        guns_borders_size = self.guns_borders_size

        if bezel_set is None and guns_borders_size is None:
            return

        if (float(self.resolution.width) / float(self.resolution.height) < 1.6) and guns_borders_size is None:
            return

        # let's generate the zip file
        tmp_zip_dir.mkdir(parents=True)

        # bezels infos
        if bezel_set is None:
            if guns_borders_size is not None:
                bz_infos = None
            else:
                return
        else:
            bz_infos = self.bezel_files
            if bz_infos is None and guns_borders_size is None:
                return

        # create an empty bezel
        if bz_infos is None:
            overlay_png_file = Path('/tmp/bezel_transmame_black.png')
            create_transparent_image(overlay_png_file, self.resolution.width, self.resolution.height)
            bz_infos = BezelFiles(overlay_png_file)

        # copy the png inside
        if bz_infos.mame_zip is not None and bz_infos.mame_zip.exists():
            art_file = Path('/var/run/mame_artwork') / f'{mess_system_name if mess_system_name else self.rom.id}.zip'

            if art_file.exists():
                art_file.unlink()

            art_file.symlink_to(bz_infos.mame_zip)

            # hum, not nice if guns need borders
            return

        if bz_infos.layout is not None and bz_infos.layout.exists():
            (tmp_zip_dir / 'default.lay').symlink_to(bz_infos.layout)
            png_file = tmp_zip_dir / bz_infos.png.name
            png_file.symlink_to(bz_infos.png)
            image_width, image_height = get_image_size(bz_infos.png)
        else:
            png_file = tmp_zip_dir / 'default.png'
            png_file.symlink_to(bz_infos.png)

            if bz_infos.info is not None and bz_infos.info.exists():
                bz_info_data = json.loads(bz_infos.info.read_text())

                image_width: int = bz_info_data['width']
                image_height: int = bz_info_data['height']
                bz_y: int = bz_info_data['top']
                bz_x: int = bz_info_data['left']
                bz_bottom: int = bz_info_data['bottom']
                bz_right: int = bz_info_data['right']
                bz_alpha: float = bz_info_data.get('opacity', 1.0)  # Just in case it's not set in the info file

                bz_width = image_width - bz_x - bz_right
                bz_height = image_height - bz_y - bz_bottom
            else:
                image_width, image_height = get_image_size(bz_infos.png)
                _, _, rotate = await get_machine_size(self.rom.id, tmp_zip_dir)

                # assumes that all bezels are setup for 4:3H or 3:4V aspects
                if rotate == 270 or rotate == 90:
                    bz_width = int(image_height * (3 / 4))
                else:
                    bz_width = int(image_height * (4 / 3))
                bz_height = image_height
                bz_x = int((image_width - bz_width) / 2)
                bz_y = 0
                bz_alpha = 1.0

            (tmp_zip_dir / 'default.lay').write_text(f'''<mamelayout version="2">
    <element name="bezel"><image file="default.png" /></element>
    <view name="bezel">
        <screen index="0"><bounds x="{bz_x}" y="{bz_y}" width="{bz_width}" height="{bz_height}" /></screen>
        <element ref="bezel"><bounds x="0" y="0" width="{image_width}" height="{image_height}" alpha="{bz_alpha}" /></element>
    </view>
</mamelayout>
''')
        if (bezel_tattoo := self.config.get_str('bezel.tattoo', '0')) != '0':
            tattoo: Image.Image | None = None

            if bezel_tattoo == 'system':
                tattoo_file = BATOCERA_SHARE_DIR / 'controller-overlays' / f'{self.system}.png'
                if not tattoo_file.exists():
                    tattoo_file = BATOCERA_SHARE_DIR / 'controller-overlays' / 'generic.png'

                try:
                    tattoo = Image.open(tattoo_file)
                except Exception:
                    _logger.error('Error opening controller overlay: %s', tattoo_file)

            elif (
                bezel_tattoo == 'custom'
                and (bezel_tattoo_file := self.config.get_str('bezel.tattoo_file'))
                and (tattoo_file := Path(bezel_tattoo_file)).exists()
            ):
                try:
                    tattoo = Image.open(tattoo_file)
                except Exception:
                    _logger.error('Error opening custom file: %s', tattoo_file)
            else:
                tattoo_file = BATOCERA_SHARE_DIR / 'controller-overlays' / 'generic.png'
                try:
                    tattoo = Image.open(tattoo_file)
                except Exception:
                    _logger.error('Error opening custom file: %s', tattoo_file)

            if tattoo is not None:
                output_png_file = Path('/tmp/bezel_tattooed.png')
                back = Image.open(png_file)
                tattoo = tattoo.convert('RGBA')
                back = back.convert('RGBA')
                tw, th = get_image_size(tattoo_file)
                tatwidth = int(
                    240 / 1920 * image_width
                )  # 240 = half of the difference between 4:3 and 16:9 on 1920px (0.5*1920/16*4)
                pcent = float(tatwidth / tw)
                tatheight = int(float(th) * pcent)
                tattoo = tattoo.resize((tatwidth, tatheight), Image.Resampling.LANCZOS)  # pyright: ignore[reportUnknownMemberType]
                alphatat = tattoo.split()[-1]
                corner = self.config.get_str('bezel.tattoo_corner', 'NW')
                if corner.upper() == 'NE':
                    back.paste(tattoo, (image_width - tatwidth, 20), alphatat)  # 20 pixels vertical margins (on 1080p)
                elif corner.upper() == 'SE':
                    back.paste(tattoo, (image_width - tatwidth, image_height - tatheight - 20), alphatat)
                elif corner.upper() == 'SW':
                    back.paste(tattoo, (0, image_height - tatheight - 20), alphatat)
                else:  # default = NW
                    back.paste(tattoo, (0, 20), alphatat)
                imgnew = Image.new('RGBA', (image_width, image_height), (0, 0, 0, 255))
                imgnew.paste(back, (0, 0, image_width, image_height))
                imgnew.save(output_png_file, mode='RGBA', format='PNG')

                try:
                    png_file.unlink()
                except Exception:
                    pass

                png_file.symlink_to(output_png_file)

        # borders for guns
        if guns_borders_size is not None:
            output_png_file = Path('/tmp/bezel_gunborders.png')
            create_gun_border_image(
                png_file, output_png_file, guns_borders_size, self.guns_border_ratio, inner_color=self.gun_borders_color
            )

            try:
                png_file.unlink()
            except Exception:
                pass

            png_file.symlink_to(output_png_file)

    def __get_system_args(
        self, mess_system: MessSystemInfo, mess_model: str, soft_list: str, /
    ) -> tuple[list[str | Path], str]:
        args: list[str | Path] = []
        special_controller = 'none'

        # TI-99 32k RAM expansion & speech modules - enabled by default
        if self.system == 'ti99':
            args.extend(['-ioport', 'peb'])

            if self.config.get_bool('ti99_32kram', True):
                args.extend(['-ioport:peb:slot2', '32kmem'])

            if self.config.get_bool('ti99_speech', True):
                args.extend(['-ioport', 'speechsyn'])

        # Laser 310 Memory Expansion & Joystick
        if self.system == 'laser310':
            args.extend(['-io', 'joystick', '-mem', self.config.get('memslot', 'laser_64k')])

        # BBC Joystick
        if self.system == 'bbcmicro' and (stick_type := self.config.get('sticktype', 'none')) != 'none':
            args.extend(['-analogue', stick_type])
            special_controller = stick_type

        # Enterprise
        if self.system == 'enterprise':
            args.extend(['-exp', 'exdos'])

        # Apple II
        if self.system == 'apple2':
            rom_extension = self.rom.suffix.lower()
            # only add SD/IDE control if provided a hard drive image
            if rom_extension in {'.hdv', '.2mg', '.chd', '.iso', '.bin', '.cue'}:
                args.extend(['-sl7', 'cffa202'])
            if (game_io := self.config.get('gameio', 'none')) != 'none':
                if game_io == 'joyport' and mess_model != 'apple2p':
                    _logger.debug('Joyport joystick is only compatible with Apple II Plus')
                else:
                    args.extend(['-gameio', game_io])
                    special_controller = game_io

        # RAM size (Mac excluded, special handling below)
        ram_size = self.config.get_int('ramsize')
        if self.system != 'macintosh' and ram_size:
            args.extend(['-ramsize', f'{ram_size}M'])

        # Mac RAM & Image Reader (if applicable)
        if self.system == 'macintosh' and ram_size:
            if mess_model in ['maciix', 'maclc3']:
                if mess_model == 'maclc3' and ram_size == 2:
                    ram_size = 4
                if mess_model == 'maclc3' and ram_size > 80:
                    ram_size = 80
                if mess_model == 'maciix' and ram_size == 16:
                    ram_size = 32
                if mess_model == 'maciix' and ram_size == 48:
                    ram_size = 64

                args.extend(['-ramsize', f'{ram_size}M'])

            if mess_model == 'maciix':
                image_slot = self.config.get('imagereader', 'nba')
                if image_slot != 'disabled':
                    args.extend([f'-{image_slot}', 'image'])

        alt_rom_type = self.config.get_str('altromtype')
        rom_extension = self.rom.suffix

        if not soft_list:
            # Boot disk for Macintosh
            # Will use Floppy 1 or Hard Drive, depending on the disk.
            boot_disk = self.config.get('bootdisk')
            if self.system == 'macintosh' and boot_disk:
                if boot_disk in ['macos30', 'macos608', 'macos701', 'macos75']:
                    bootType = '-flop1'
                    bootDisk = f'/userdata/bios/{boot_disk}.img'
                else:
                    bootType = '-hard'
                    bootDisk = f'/userdata/bios/{boot_disk}.chd'
                args.extend([bootType, bootDisk])

            # Alternate ROM type for systems with mutiple media (ie cassette & floppy)
            # Mac will auto change floppy 1 to 2 if a boot disk is enabled
            # Only one drive on FMTMarty
            if self.system != 'macintosh':
                if alt_rom_type:
                    if mess_model == 'fmtmarty' and alt_rom_type == 'flop1':
                        args.append('-flop')
                    else:
                        args.append(f'-{alt_rom_type}')
                elif self.system == 'adam':
                    # add some logic based on the rom extension
                    if rom_extension == '.ddp':
                        args.extend(['-cass1'])
                    elif rom_extension == '.dsk':
                        args.extend(['-flop1'])
                    else:
                        args.extend(['-cart1'])
                elif self.system in ('coco', 'dragon64'):
                    if rom_extension.casefold() == '.cas':
                        args.extend(['-cass'])
                    elif rom_extension.casefold() == '.dsk':
                        args.extend(['-flop1'])
                    else:
                        args.extend(['-cart'])
                elif self.system == 'sc3000':
                    if rom_extension.casefold() in ('.cas', '.wav', '.bit'):
                        args.extend(['-cass'])
                    else:
                        args.extend(['-cart'])
                elif self.system == 'segaai':
                    if rom_extension.casefold() in ('.wav', '.flac', '.cas'):
                        args.extend(['-cass'])
                    else:
                        args.extend(['-card'])
                elif self.system == 'mc10':
                    if rom_extension.casefold() == '.cas':
                        args.extend(['-cass'])
                    else:
                        args.extend(['-cart'])
                else:
                    args.extend([f'-{mess_system.rom_type}'])
            else:
                if boot_disk:
                    if (alt_rom_type == 'flop1' or not alt_rom_type) and boot_disk in [
                        'macos30',
                        'macos608',
                        'macos701',
                        'macos75',
                    ]:
                        args.extend(['-flop2'])
                    elif alt_rom_type:
                        args.extend([f'-{alt_rom_type}'])
                    else:
                        args.extend([f'-{mess_system.rom_type}'])
                else:
                    if alt_rom_type:
                        args.extend([f'-{alt_rom_type}'])
                    else:
                        args.extend([f'-{mess_system.rom_type}'])

            # Use the full filename for MESS ROMs
            args.extend([self.rom])
        else:
            # Prepare software lists
            _SOFT_DIR.mkdir(parents=True, exist_ok=True)
            for check_file in _SOFT_DIR.iterdir():
                if check_file.is_symlink():
                    check_file.unlink()

                if check_file.is_dir():
                    shutil.rmtree(check_file)

            _HASH_DIR.mkdir(parents=True, exist_ok=True)
            (_HASH_DIR / f'{soft_list}.xml').symlink_to(f'/usr/bin/mame/hash/{soft_list}.xml')

            if soft_list in _SUBDIR_SOFT_LIST:
                (_SOFT_DIR / soft_list).symlink_to(self.rom.parent.parents[0], target_is_directory=True)
                args.append(self.rom.parent.name)
            else:
                (_SOFT_DIR / soft_list).symlink_to(self.rom.parent, target_is_directory=True)
                args.append(self.rom.id)

        # Create & add a blank disk if needed, insert into drive 2
        # or drive 1 if drive 2 is selected manually or FM Towns Marty.
        if self.config.get_bool('addblankdisk'):
            if self.system == 'fmtowns':
                blank_disk = Path('/usr/share/mame/blank.fmtowns')
                target_folder = MAME_SAVES / self.system
                target_disk = target_folder / self.rom.id
            # Add elif statements here for other systems if enabled
            else:
                blank_disk = Path('/usr/share/mame/blank.default')
                target_folder = MAME_SAVES / self.system
                target_disk = target_folder / f'{self.rom.id}.default'

            target_folder.mkdir(parents=True, exist_ok=True)

            if not target_disk.exists():
                shutil.copy2(blank_disk, target_disk)

            # Add other single floppy systems to this if statement
            if mess_model == 'fmtmarty':
                args.extend(['-flop', target_disk])
            elif self.config.get('altromtype') == 'flop2':
                args.extend(['-flop1', target_disk])
            else:
                args.extend(['-flop2', target_disk])

        return args, special_controller

    def generate_pad_sequence(
        self,
        controller: Controller,
        key: str,
        /,
        *,
        reversed: bool = False,
        ignore_axis: bool = False,
        mapping: str = '',
        player_number: int = 1,
        input_key: str | None = None,
    ) -> str:
        lookup = input_key if input_key is not None else key

        if reversed:
            lookup = reverse_mapping(lookup) or lookup

        if lookup not in controller.inputs:
            return 'unknown'

        is_wheel = self.config.use_wheels and any(
            wheel.joystick_index == controller.index for wheel in self.wheels.values()
        )
        sequence = get_input_definition(
            controller,
            controller.inputs[lookup],
            key,
            reversed,
            control_scheme=self.mame_control_scheme,
            ignore_axis=ignore_axis,
            is_wheel=is_wheel,
        )

        _mappings, gun_mappings, mouse_mappings = self.all_mame_control_mappings

        if mapping in gun_mappings:
            sequence += f' OR GUNCODE_{player_number}_{gun_mappings[mapping]}'
            if gun_mappings[mapping] == 'BUTTON2' and (pedal_key := self._pedal_key(player_number)) is not None:
                sequence += f' OR KEYCODE_{pedal_key.upper()}'

        if mapping in mouse_mappings:
            mouse_player = player_number if self.config.get_bool('multimouse') else 1
            sequence += f' OR MOUSECODE_{mouse_player}_{mouse_mappings[mapping]}'

        if mapping == 'COIN':
            sequence += f' OR KEYCODE_{player_number}_{player_number + 4}'

        return sequence

    def _pedal_key(self, player_number: int, /) -> str | None:
        pedal_cname = f'controllers.pedals{player_number}'

        if pedal_cname in self.config:
            return self.config[pedal_cname]

        return _PEDAL_KEYS.get(player_number)

    def can_reverse_pad_mapping(self, controller: Controller, reversed_key: str, /) -> bool:
        return reversed_key in controller.inputs

    def adjust_control_mappings(self, controller: Controller, mappings: dict[str, str], /) -> dict[str, str]:
        if not self.config.use_wheels or not any(
            wheel.joystick_index == controller.index for wheel in self.wheels.values()
        ):
            return mappings

        _logger.debug('controller %s has a wheel', controller.index + 1)
        mappings_use = {name: key for name, key in mappings.items() if key not in {'l2', 'r2', 'joystick1left'}}
        mappings_use['PEDAL'] = 'r2'
        mappings_use['PEDAL2'] = 'l2'
        mappings_use['PADDLE'] = 'joystick1left'

        return mappings_use

    def prepare_control_config(self, config: ControlConfig, /) -> None:
        config.initialize_crosshairs(self.config.get_str('mame_crosshair'))

    def prepare_player_config(self, config: ControlConfig, player_number: int, /) -> None:
        config.add_common_player_ports(player_number)

    def extra_start_coin_port_type(self, mapping: str, player_number: int, /) -> str | None:
        if mapping == 'START':
            return f'P{player_number}_START'
        if mapping == 'COIN':
            return f'P{player_number}_SELECT'
        return None

    def cdi_screen_view(self) -> str:
        return 'Main Screen Standard (4:3)' if self.bezel_set == 'none' else 'Upright_Artwork'

    def should_overwrite_system_cfg(self, cfg_path: Path, mess_system_name: str, alt_cfg_exists: bool, /) -> bool:
        custom_config = self.config.get_bool('customcfg')
        per_game_config = cfg_path != (MAME_CONFIG / mess_system_name)
        return not (alt_cfg_exists and (custom_config or per_game_config))

    def finish_control_config(self, config: ControlConfig, /) -> None:
        if not self.config.use_guns or len(self.guns) <= len(self.controllers):
            return

        _mappings, gun_mappings, _mouse_mappings = self.all_mame_control_mappings

        for gun_number in range(len(self.controllers) + 1, len(self.guns) + 1):
            pedal_key = self._pedal_key(gun_number)
            config.add_common_player_ports(gun_number)

            for mapping in gun_mappings:
                config.add_gun_port(gun_number, mapping, gun_mappings, pedal_key)

    def ui_combo_input(self, controller: Controller, ui_type: str, mapped_key: str, /) -> tuple[str, bool]:
        if has_stick(controller) and ui_type in {'UI_DOWN', 'UI_RIGHT'}:
            return mapped_key, True

        return mapped_key, False
