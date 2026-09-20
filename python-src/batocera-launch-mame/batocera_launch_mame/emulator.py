from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Final

from batocera_common.dataclasses import cached_dataclass
from batocera_common.paths import BIOS, CONFIGS, ROMS, SAVES, SCREENSHOTS
from batocera_launch import Command
from batocera_launch.paths import USER_DECORATIONS
from batocera_launch_mame_common import MessSystemInfo, get_autorun_command
from batocera_launch_mame_common.paths import MAME_BIN_DIR

from .base import MAMEBase
from .bezels import MAMEBezels
from .controllers import MAMEControllers

_logger: Final = logging.getLogger(__name__)

_SOFT_DIR: Final = Path('/var/run/mame_software')
_HASH_DIR: Final = _SOFT_DIR / 'hash'
_SUBDIR_SOFT_LIST: Final = ['mac_hdd', 'bbc_hdd', 'cdi', 'archimedes_hdd', 'fmtowns_cd']


@cached_dataclass
class MAME(MAMEControllers, MAMEBezels, MAMEBase):
    async def configure(self) -> Command:
        for path in [
            self.config_dir,
            self.saves_dir / 'nvram',
            self.saves_dir / 'cfg',
            self.saves_dir / 'input',
            self.saves_dir / 'state',
            self.saves_dir / 'diff',
            self.saves_dir / 'comments',
            self.bios_dir / 'artwork' / 'crosshairs',
            self.cheats_dir,
            self.saves_dir / 'plugins',
            self.config_dir / 'ctrlr',
            self.config_dir / 'ini',
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
            args.extend(['-rompath', f'{self.rom.parent};{self.bios_dir};{BIOS}'])
        else:
            if soft_list in _SUBDIR_SOFT_LIST:
                args.extend(['-rompath', f'{self.rom.parent};{self.bios_dir};{BIOS};{self.roms_dir};{_SOFT_DIR}'])
            else:
                args.extend(['-rompath', f'{self.rom.parent};{self.bios_dir};{BIOS};{self.roms_dir}'])

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
                f'{MAME_BIN_DIR / "plugins"};{self.saves_dir / "plugins"}',
                '-samplepath',
                self.bios_dir / 'samples',
                '-artpath',
                f'/var/run/mame_artwork/;{MAME_BIN_DIR / "artwork"};{self.bios_dir / "artwork"};{USER_DECORATIONS}',
                # Enable cheats
                '-cheat',
                '-cheatpath',
                self.cheats_dir,
                # Use full MAME logging when debug logging is enabled, else oslog. Verbose
                # logging also enables debug pop up messages during gameplay.
                '-verbose' if self.es_settings.get_str('LogLevel') == 'debug' else '-oslog',
                # MAME saves a lot of stuff, we need to map this on /userdata/saves/mame/<subfolder> for each one
                '-nvram_directory',
                self.saves_dir / 'nvram',
            ]
        )

        # Set custom config path if option is selected or default path if not
        custom_cfg = self.config.get_bool('customcfg')

        config_path = (self.config_dir / mess_system.name) if mess_system is not None else self.config_dir
        config_path = (config_path / 'custom') if custom_cfg else config_path

        config_path.mkdir(parents=True, exist_ok=True)

        # MAME will create custom configs per game for MAME ROMs and MESS ROMs with no system attached (LCD games, TV games, etc.)
        # This will allow an alternate config path per game for MESS console/computer ROMs that may need additional config.
        if self.config.get_bool('pergamecfg') and mess_system is not None and mess_system.name:
            config_path = self.config_dir / mess_system.name / self.rom.name
            config_path.mkdir(parents=True, exist_ok=True)

        args.extend(
            [
                '-cfg_directory',
                config_path,
                '-input_directory',
                self.saves_dir / 'input',
                '-state_directory',
                self.saves_dir / 'state',
                '-snapshot_directory',
                SCREENSHOTS,
                '-diff_directory',
                self.saves_dir / 'diff',
                '-comment_directory',
                self.saves_dir / 'comments',
                '-homepath',
                self.saves_dir / 'plugins',
                '-ctrlrpath',
                self.config_dir / 'ctrlr',
                '-inipath',
                f'{self.config_dir};{self.config_dir / "ini"}',
                '-crosshairpath',
                self.bios_dir / 'artwork' / 'crosshairs',
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
            args.extend(['-switchres_ini', '-modeline_generation', '-changeres', '-modesetting', '-readconfig'])
        else:
            # GroovyMAME enables switchres by default; its xrandr mode restore breaks rotated displays
            args.extend(['-noswitchres', '-resolution', f'{self.resolution.width}x{self.resolution.height}'])

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
            screens = await self.screens
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
                self.config_dir,
                self.system,
                self.rom,
                mess_system,
                self.config.get_str('altromtype'),
                soft_list,
            )
            if autorun_command:
                if autorun_command.startswith("'"):
                    autorun_command = autorun_command.replace("'", '')

                args.extend(['-autoboot_delay', str(autorun_delay), '-autoboot_command', autorun_command])

        self.write_control_config(config_path, mess_model, special_controller, custom_cfg)

        # If user provided a custom cmd file at the default location, use that as the customized commandArray
        if (default_custom_cmd_filepath := Path(f'{self.rom}.cmd')).is_file():
            args = default_custom_cmd_filepath.read_text().splitlines()  # pyright: ignore[reportAssignmentType]

        return Command(args, {'PWD': MAME_BIN_DIR, 'XDG_CONFIG_HOME': CONFIGS, 'XDG_CACHE_HOME': SAVES})

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
                args.append(self.rom.stem)

        # Create & add a blank disk if needed, insert into drive 2
        # or drive 1 if drive 2 is selected manually or FM Towns Marty.
        if self.config.get_bool('addblankdisk'):
            if self.system == 'fmtowns':
                blank_disk = Path('/usr/share/mame/blank.fmtowns')
                target_folder = self.saves_dir / self.system
                target_disk = target_folder / self.rom.stem
            # Add elif statements here for other systems if enabled
            else:
                blank_disk = Path('/usr/share/mame/blank.default')
                target_folder = self.saves_dir / self.system
                target_disk = target_folder / f'{self.rom.stem}.default'

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
