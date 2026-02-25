from __future__ import annotations

import logging
import re
import shutil
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final

from batocera_common import vulkan
from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dict import merge
from batocera_common.fs import directory_differences
from batocera_common.paths import BIOS, CACHE, CONFIGS
from batocera_common.yaml import safe_dump_yaml12, safe_load_yaml12
from batocera_launch.command import Command
from batocera_launch.emulator import Emulator
from batocera_launch.exceptions import BatoceraException
from batocera_launch.paths import configure_emulator
from batocera_launch_rpcs3.controllers import generate_controllers_config
from batocera_launch_rpcs3.paths import (
    RPCS3_BIN,
    RPCS3_CONFIG,
    RPCS3_CONFIG_DIR,
    RPCS3_CURRENT_CONFIG,
    RPCS3_DEV_HDD0_DIR,
    RPCS3_VFS_CONFIG,
)
from batocera_launch_rpcs3.sfo import SFO

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_launch.types import HotkeysContext

_logger = logging.getLogger(__name__)

# USB device tuning for the arcade PS3 titles (System 357/369, Taiko, ...) shipped as a
# PSN squashfs. These all share the SCEEXE000 title-id, so they cannot be told apart by
# their dev_hdd0/game/<id> directory; instead they are matched on the PARAM.SFO TITLE.
# Each entry maps a /dev_usbNNN slot to the emulated USB I/O board id (Serial/VID/PID);
# the slot Path is filled at runtime from the squashfs overlay when it ships that folder.
# NOTE: keys must be the exact PARAM.SFO TITLE. Only "DarkEscape" is confirmed so far;
# the others are keyed by their working name pending the real TITLE value.
_ARCADE_USB_CONFIG: Final[dict[str, dict[str, dict[str, str]]]] = {
    'DarkEscape': {
        '/dev_usb000': {'Serial': '268611070000', 'VID': '0b9a', 'PID': '0c00'},
    },
    'TEKKEN6': {
        '/dev_usb000': {'Serial': '76C0D0000000', 'VID': '0693', 'PID': '0026'},
        '/dev_usb007': {'Serial': '76C0D0003038', 'VID': '0693', 'PID': '0026', 'Path': ''},
    },
    'TEKKEN6BR': {
        '/dev_usb000': {'Serial': '026450800000', 'VID': '0693', 'PID': '0026'},
        '/dev_usb007': {'Serial': '76C0D0003038', 'VID': '0693', 'PID': '0026', 'Path': ''},
    },
    'RazingStorm': {
        '/dev_usb000': {'Serial': '026391000000', 'VID': '0693', 'PID': '0026'},
    },
    'Sailor zombie': {
        '/dev_usb000': {'Serial': '271711170000', 'VID': '0b9a', 'PID': '0c10'},
    },
    'DZB3': {
        '/dev_usb000': {'Serial': '267210000000', 'VID': '0B9A', 'PID': '0C00'},
    },
    'Deadstorm Pirates Special Edition': {
        '/dev_usb000': {'Serial': '272311000000', 'VID': '0B9A', 'PID': '0C00'},
    },
    # Tekken Tag Tournament 2 and its Unlimited revision share the same TITLE.
    'TEKKEN TAG TOURNAMENT 2': {
        '/dev_usb000': {'Serial': '267910000000', 'VID': '0B9A', 'PID': '0C00'},
    },
    # Taiko no Tatsujin variants all share the same I/O board ids.
    **{
        taiko: {
            '/dev_usb000': {'Serial': '000000000000', 'VID': '13fe', 'PID': '4100'},
            '/dev_usb001': {'Serial': '268411060021', 'VID': '0b9a', 'PID': '0c00'},
        }
        for taiko in (
            'Taiko no Tatsujin',  # Sorairo Version
            'Taiko no Tatsujin(S101)',  # Blue Version
            'Taiko no Tatsujin(S111)',  # Green Version
            'Taiko no Tatsujin(ST41)',  # Momoiro Version
            'Taiko no Tatsujin(ST48)',  # Wadaiko Master
            'Taiko no Tatsujin(ST51)',  # Kimidori Version
            'Taiko no Tatsujin(ST61)',  # Murasaki Version
            'Taiko no Tatsujin(ST71)',  # White Version
            'Taiko no Tatsujin(ST87)',  # Red Version
            'Taiko no Tatsujin(ST91)',  # Yellow Version
        )
    },
}


def _get_firmware_version() -> str | None:
    try:
        with (RPCS3_CONFIG_DIR / 'dev_flash' / 'vsh' / 'etc' / 'version.txt').open('r') as stream:
            lines = stream.readlines()
        for line in lines:
            matches = re.match('^release:(.*):', line)
            if matches:
                return matches[1]
    except Exception:
        return None
    return None


def _migrate_dev_hdd0() -> None:
    legacy_dev_hdd0 = RPCS3_CONFIG_DIR / 'dev_hdd0'
    if not legacy_dev_hdd0.exists():
        # New install or fully migrated: nothing to do
        return

    if RPCS3_DEV_HDD0_DIR.exists():
        # Partial or failed migration: leave it alone
        _logger.warning('Skipping RPCS3 dev_hdd0 migration: target directory already exists at %s', RPCS3_DEV_HDD0_DIR)
        return

    RPCS3_DEV_HDD0_DIR.parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.copytree(legacy_dev_hdd0, RPCS3_DEV_HDD0_DIR)
    except Exception:
        _logger.exception('Failed to copy RPCS3 dev_hdd0 from %s to %s', legacy_dev_hdd0, RPCS3_DEV_HDD0_DIR)
        return

    _logger.debug('Successfully copied RPCS3 dev_hdd0 from %s to %s', legacy_dev_hdd0, RPCS3_DEV_HDD0_DIR)

    differences = directory_differences(legacy_dev_hdd0, RPCS3_DEV_HDD0_DIR)
    if differences:
        _logger.error('RPCS3 dev_hdd0 migration verification failed:\n%s', differences.report())
        return

    _logger.debug('Verified RPCS3 dev_hdd0 migration from %s to %s', legacy_dev_hdd0, RPCS3_DEV_HDD0_DIR)

    shutil.rmtree(legacy_dev_hdd0)

    _logger.debug('Completed RPCS3 dev_hdd0 migration from %s to %s', legacy_dev_hdd0, RPCS3_DEV_HDD0_DIR)


@dataclass(slots=True)
class RPCS3(Emulator):
    @property
    def hotkeygen_context(self) -> HotkeysContext:
        return {'name': 'rpcs3', 'keys': {'exit': '/usr/bin/rpcs3-exit', 'menu': ['KEY_LEFTSHIFT', 'KEY_F10']}}

    @property
    def needs_overlayfs(self) -> bool:
        return True

    @property
    def closest_screen_ratio(self) -> str:
        screen_ratio = self.resolution.width / self.resolution.height
        return '4:3' if screen_ratio < 1.6 else '16:9'

    def _generate_vfs_config(self, prepared_rom: Path, is_psn_squashfs: bool, arcade_game_title: str | None, /) -> None:
        rom_dev_hdd0 = prepared_rom / 'dev_hdd0'
        rom_dev_hdd1 = prepared_rom / 'dev_hdd1'
        arcade_usb_config = _ARCADE_USB_CONFIG.get(arcade_game_title or '', {})

        dev_hdd0 = f'{rom_dev_hdd0 if is_psn_squashfs else RPCS3_DEV_HDD0_DIR}/'
        # For a PSN squashfs, redirect /dev_hdd1/ to the overlay when it ships one.
        dev_hdd1 = f'{rom_dev_hdd1 if is_psn_squashfs and rom_dev_hdd1.is_dir() else "$(EmulatorDir)dev_hdd1"}/'

        # Build the full /dev_usb***/ block (slots 000-007). Every tuned slot (one carrying
        # an emulated USB I/O board Serial/VID/PID) reads its data from the overlay's single
        # dev_usb000 folder, so its Path defaults there; a slot may override "Path" (e.g. ""
        # for a pure passthrough device). Untuned dev_usb000 keeps the RPCS3 default mount
        # (or the overlay folder if shipped) and the rest stay empty.
        overlay_usb000_dir = prepared_rom / 'dev_usb000'
        overlay_usb000 = f'{overlay_usb000_dir}/'

        if arcade_game_title is not None and arcade_usb_config:
            overlay_usb000_dir.mkdir(parents=True, exist_ok=True)

        usb_config: dict[str, dict[str, str]] = {}

        for index in range(8):
            slot = f'/dev_usb00{index}'
            slot_usb_config = arcade_usb_config.get(slot, {})
            usb_dir = prepared_rom / f'dev_usb00{index}'

            if slot_usb_config:
                path = slot_usb_config.get('Path', overlay_usb000 if is_psn_squashfs else '')
            elif is_psn_squashfs and usb_dir.is_dir():
                path = f'{usb_dir}/'
            elif not index:
                path = '$(EmulatorDir)dev_usb000/'
            else:
                path = ''

            usb_config[slot] = {
                'Path': path,
                'Serial': slot_usb_config.get('Serial', ''),
                'VID': slot_usb_config.get('VID', ''),
                'PID': slot_usb_config.get('PID', ''),
            }

        safe_dump_yaml12(
            {
                '$(EmulatorDir)': '',
                '/dev_hdd0/': dev_hdd0,
                '/dev_hdd1/': dev_hdd1,
                '/dev_flash/': '$(EmulatorDir)dev_flash/',
                '/dev_flash2/': '$(EmulatorDir)dev_flash2/',
                '/dev_flash3/': '$(EmulatorDir)dev_flash3/',
                '/dev_bdvd/': '$(EmulatorDir)dev_bdvd/',
                '/games/': '$(EmulatorDir)games/',
                '/app_home/': '',
                '/dev_usb***/': usb_config,
            },
            RPCS3_VFS_CONFIG,
        )

    def configure(self, prepared_rom: Path, /) -> Command:
        _migrate_dev_hdd0()

        RPCS3_DEV_HDD0_DIR.mkdir(parents=True, exist_ok=True)

        sfo = SFO.from_rom(prepared_rom)

        rom_dev_hdd0 = prepared_rom / 'dev_hdd0'
        rom_game_dir = rom_dev_hdd0 / 'game'

        rom_name: Path | None = None

        # Detect PSN game packed as a squashfs: emulatorlauncher has already mounted the
        # squashfs and (via writesToRom=True) created a writable overlayfs, so rom is
        # /var/run/overlays/<stem> mirroring the dev_hdd0 layout.
        is_psn_squashfs = prepared_rom.is_dir() and str(prepared_rom).startswith('/var/run/') and rom_game_dir.is_dir()
        arcade_game_title = (
            sfo.TITLE
            if is_psn_squashfs
            and (rom_game_dir / 'SCEEXE000' / 'PARAM.SFO').is_file()
            and sfo.TITLE is not None
            and sfo.TITLE in _ARCADE_USB_CONFIG
            else None
        )

        if arcade_game_title is not None:
            _logger.debug("Matched RPCS3 arcade title '%s'", arcade_game_title)

        generate_controllers_config(self.config, self.controllers, keyboard=bool(arcade_game_title))

        # Taking care of the CurrentSettings.ini file
        RPCS3_CURRENT_CONFIG.parent.mkdir(parents=True, exist_ok=True)

        # Generates CurrentSettings.ini with values to disable prompts on first run
        current_settings = CaseSensitiveConfigParser(interpolation=None)
        if RPCS3_CURRENT_CONFIG.exists():
            current_settings.read(RPCS3_CURRENT_CONFIG)

        # Sets Gui Settings to close completely and disables some popups
        if not current_settings.has_section('main_window'):
            current_settings.add_section('main_window')

        current_settings.set('main_window', 'confirmationBoxExitGame', 'false')
        current_settings.set('main_window', 'infoBoxEnabledInstallPUP', 'false')
        current_settings.set('main_window', 'infoBoxEnabledWelcome', 'false')

        with RPCS3_CURRENT_CONFIG.open('w') as configfile:
            current_settings.write(configfile)

        RPCS3_CONFIG.parent.mkdir(parents=True, exist_ok=True)

        # Generate a default config if it doesn't exist otherwise just open the existing
        rpcs3_yml_config: dict[str, dict[str, Any]] = {}
        if RPCS3_CONFIG.is_file():
            rpcs3_yml_config = safe_load_yaml12(RPCS3_CONFIG, dict[str, dict[str, Any]]) or {}

        # VFS is no longer stored in config.yml: RPCS3 reads it from a dedicated vfs.yml
        # file. Drop any stale VFS section that older versions may have written here.
        rpcs3_yml_config.pop('VFS', None)

        # Add Nodes if not in the file
        if 'Core' not in rpcs3_yml_config:
            rpcs3_yml_config['Core'] = {}
        if 'Video' not in rpcs3_yml_config:
            rpcs3_yml_config['Video'] = {}
        if 'Audio' not in rpcs3_yml_config:
            rpcs3_yml_config['Audio'] = {}
        if 'Input/Output' not in rpcs3_yml_config:
            rpcs3_yml_config['Input/Output'] = {}
        if 'System' not in rpcs3_yml_config:
            rpcs3_yml_config['System'] = {}
        if 'Net' not in rpcs3_yml_config:
            rpcs3_yml_config['Net'] = {}
        if 'Savestate' not in rpcs3_yml_config:
            rpcs3_yml_config['Savestate'] = {}
        if 'Miscellaneous' not in rpcs3_yml_config:
            rpcs3_yml_config['Miscellaneous'] = {}
        if 'Log' not in rpcs3_yml_config:
            rpcs3_yml_config['Log'] = {}

        vulkan_available = vulkan.is_available()
        backend = self.config.get('rpcs3_gfxbackend', 'Vulkan') if vulkan_available else 'OpenGL'

        if vulkan_available:
            _logger.debug('Vulkan driver is available on the system.')

            if backend == 'OpenGL':
                _logger.debug('User selected OpenGL')
        else:
            _logger.debug('Vulkan driver is not available on the system. Falling back to OpenGL')

        match self.config.get('rpcs3_framelimit'):
            case None:
                frame_limit = 'Auto'
                second_frame_limit = 0
            # Check for valid Frame Limit value, if it's not a Frame Limit value apply to Second Frame Limit
            case 'Off' | '30' | '50' | '59.94' | '60' as rpcs3_framelimit:
                frame_limit = rpcs3_framelimit
                second_frame_limit = 0
            case _ as rpcs3_framelimit:
                frame_limit = 'Off'
                second_frame_limit = rpcs3_framelimit

        match self.config.get('rpcs3_zcull'):
            case 'Approximate':
                accurate_zcull_stats = False
                relaxed_zcull_sync = False
            case 'Relaxed':
                accurate_zcull_stats = False
                relaxed_zcull_sync = True
            case _:
                accurate_zcull_stats = True
                relaxed_zcull_sync = False

        time_stretch = self.config.get_bool('rpcs3_timestretch')

        config: dict[str, Any] = {
            'Core': {
                # Set the PPU Decoder based on config
                'PPU Decoder': self.config.get('rpcs3_ppudecoder', 'Recompiler (LLVM)'),
                # Set the SPU Decoder based on config
                'SPU Decoder': self.config.get('rpcs3_spudecoder', 'Recompiler (LLVM)'),
                # Set the SPU XFloat Accuracy based on config
                'XFloat Accuracy': self.config.get('rpcs3_spuxfloataccuracy', 'Approximate'),
                # Force to True for now to account for updates where exiting config file present. (True results in less stutter when a SPU module is in cache)
                'SPU Cache': True,
                # Preferred SPU Threads
                'Preferred SPU Threads': self.config.get_int('rpcs3_sputhreads', 0),
                # SPU Loop Detection
                'SPU loop detection': self.config.get_bool('rpcs3_spuloopdetection'),
                # SPU Block Size
                'SPU Block Size': self.config.get('rpcs3_spublocksize', 'Safe'),
                # Max Power Saving CPU-Preemptions
                # values are maximum yields per frame threshold
                'Max CPU Preempt Count': self.config.get_int('rpcs3_maxcpu_preemptcount', 0),
                # Sleep Timers Accuracy
                'Sleep Timers Accuracy': self.config.get('rpcs3_sleep_timers_accuracy', 'As Host'),
            },
            'Video': {
                'Renderer': backend,
                # System aspect ratio (the setting in the PS3 system itself, not the displayed ratio) a.k.a. TV mode.
                # If not set, see if the screen ratio is closer to 4:3 or 16:9 and pick that.
                'Aspect ratio': self.config.get('rpcs3_ratio') or self.closest_screen_ratio,
                # Shader compilation
                'Shader Mode': self.config.get('rpcs3_shadermode', 'Async Shader Recompiler'),
                # Vsync
                'VSync': self.config.get_bool('rpcs3_vsync'),
                # Stretch to display area
                'Stretch To Display Area': self.config.get_bool('rpcs3_stretchdisplay'),
                # Frame Limit
                # Frame limit checks for specific values("Auto", "Off", "30", "50", "59.94", "60")
                # Second Frame Limit can be any float/integer. 0 = disabled.
                'Frame limit': frame_limit,
                'Second Frame Limit': second_frame_limit,
                # Write Color Buffers
                'Write Color Buffers': self.config.get_bool('rpcs3_colorbuffers'),
                # Read Color Buffers
                'Read Color Buffers': self.config.get_bool('rpcs3_read_colorbuffers'),
                # Disable Vertex Cache
                'Disable Vertex Cache': self.config.get_bool('rpcs3_vertexcache'),
                # Anisotropic Filtering
                'Anisotropic Filter Override': self.config.get_int('rpcs3_anisotropic', 0),
                # MSAA
                'MSAA': self.config.get('rpcs3_aa', 'Auto'),
                # ZCULL
                'Accurate ZCULL stats': accurate_zcull_stats,
                'Relaxed ZCULL Sync': relaxed_zcull_sync,
                # Shader Precision
                'Shader Precision': self.config.get('rpcs3_shader', 'High'),
                # Internal resolution (CHANGE AT YOUR OWN RISK)
                'Resolution': '1280x720',
                # Resolution scaling
                'Resolution Scale': self.config.get_int('rpcs3_resolution_scale', 100),
                # Resolution scale threshold
                'Minimum Scalable Dimension': int(self.config.get_float('rpcs3_resolution_scale_threshold', 16)),
                # Output Scaling
                'Output Scaling Mode': self.config.get('rpcs3_scaling', 'Bilinear'),
                # Number of Shader Compilers
                'Shader Compiler Threads': self.config.get_int('rpcs3_num_compilers', 0),
                # Multithreaded RSX
                'Multithreaded RSX': self.config.get_bool('rpcs3_rsx'),
                # Write Depth Buffer
                'Write Depth Buffer': self.config.get_bool('rpcs3_write_depth_buffers'),
                # Force CPU blit emulation
                'Force CPU Blit': self.config.get_bool('rpcs3_force_cpu_blit_emulation'),
            },
            'Audio': {
                # defaults
                'Renderer': 'Cubeb',
                'Master Volume': 100,
                # audio format
                'Audio Format': self.config.get('rpcs3_audio_format', 'Automatic'),
                # convert to 16 bit
                'Convert to 16 bit': self.config.get_bool('rpcs3_audio_16bit'),
                # audio buffering
                'Enable Buffering': time_stretch or self.config.get_bool('rpcs3_audiobuffer', True),
                # audio buffer duration
                'Desired Audio Buffer Duration': self.config.get_int('rpcs3_audiobuffer_duration', 100),
                # time stretching
                'Enable Time Stretching': time_stretch,
                'Time Stretching Threshold': self.config.get_int('rpcs3_timestretch_threshold', 75),
            },
            'Input/Output': {
                **(
                    {
                        'Move': 'Gun',
                        'Camera': 'Fake',
                        'Camera type': 'PS Eye',
                    }
                    if self.config.use_guns and self.guns
                    else {}
                ),
                'Show move cursor': self.config.get_bool('rpcs3_crosshairs'),
            },
            'Miscellaneous': {
                'Exit RPCS3 when process finishes': True,
                'Start games in fullscreen mode': True,
                'Show shader compilation hint': False,
                'Prevent display sleep while running games': True,
                'Show trophy popups': False,
            },
        }

        if backend == 'Vulkan':
            vulkan_config = config['Video']['Vulkan'] = {}

            if vulkan.has_discrete_gpu():
                _logger.debug('A discrete GPU is available on the system. We will use that for performance')
                discrete_name = vulkan.get_discrete_gpu_name()
                if discrete_name:
                    _logger.debug('Using Discrete GPU Name: %s for RPCS3', discrete_name)
                    vulkan_config['Adapter'] = discrete_name
                else:
                    _logger.debug("Couldn't get discrete GPU Name")
            else:
                _logger.debug('Discrete GPU is not available on the system. Using default.')

            vulkan_config['Asynchronous Texture Streaming 2'] = self.config.get_bool('rpcs3_async_texture')

        merge(rpcs3_yml_config, config)

        safe_dump_yaml12(rpcs3_yml_config, RPCS3_CONFIG)

        if self.config.use_guns and self.guns:
            # D-Pad mapping is face buttons of the PS Move △ =up ✕ =down □ =left ○ =right
            gun_mapping = {
                'T': 1,
                'Move': 2,
                'Start': 3,
                'Select': 4,
                'Triangle': 8,
                'Cross': 9,
                'Square': 10,
                'Circle': 11,
            }
            safe_dump_yaml12(
                {
                    f'Player {player}': {key: f'Gun Button {value}' for key, value in gun_mapping.items()}
                    for player in range(1, 5)
                },
                RPCS3_CONFIG_DIR / 'gem_gun.yml',
            )

        self._generate_vfs_config(prepared_rom, is_psn_squashfs, arcade_game_title)

        # copy icon files to config
        icon_target = RPCS3_CONFIG_DIR / 'Icons'
        icon_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree('/usr/share/rpcs3/Icons/', icon_target, dirs_exist_ok=True, copy_function=shutil.copy2)

        # determine the rom name
        if prepared_rom.suffix == '.psn':
            with prepared_rom.open() as fp:
                for line in fp:
                    if len(line) >= 9:
                        rom_name = RPCS3_DEV_HDD0_DIR / 'game' / line.strip().upper() / 'USRDIR' / 'EBOOT.BIN'

            if rom_name is None:
                raise BatoceraException(f'No game ID found in {prepared_rom}')
        elif is_psn_squashfs:
            # rom is /var/run/overlays/<stem>; dev_hdd0 is redirected there via vfs.yml.
            # Scan for the game ID directory and pass EBOOT.BIN directly to RPCS3.
            for game_id_dir in rom_game_dir.iterdir():
                eboot = game_id_dir / 'USRDIR' / 'EBOOT.BIN'
                if eboot.exists():
                    rom_name = eboot
                    break

            if rom_name is None:
                raise BatoceraException(f'No PSN game found in squashfs {prepared_rom}')
        elif prepared_rom.suffix.lower() == '.iso':
            rom_name = prepared_rom
        elif not configure_emulator(prepared_rom):
            rom_name = prepared_rom / 'PS3_GAME' / 'USRDIR' / 'EBOOT.BIN'

        args: list[Path | str] = [RPCS3_BIN, rom_name] if rom_name else [RPCS3_BIN]

        if not self.config.get_bool('rpcs3_gui') and rom_name:
            args.append('--no-gui')

        # firmware not installed and available : instead of starting the game, install it
        if _get_firmware_version() is None and (BIOS / 'PS3UPDAT.PUP').exists():
            args = [RPCS3_BIN, '--installfw', BIOS / 'PS3UPDAT.PUP']

        return Command(args, {'XDG_CONFIG_HOME': CONFIGS, 'XDG_CACHE_HOME': CACHE})
