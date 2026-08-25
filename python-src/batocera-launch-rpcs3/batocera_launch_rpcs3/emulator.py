from __future__ import annotations

import asyncio
import filecmp
import logging
import re
import shutil
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, Self, cast

import aiohttp
from ruamel.yaml import YAML

from batocera_common import vulkan
from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.dict import merge
from batocera_common.fs import directory_differences
from batocera_common.paths import BIOS, CACHE, CONFIGS
from batocera_common.yaml import safe_dump_yaml12, safe_load_yaml12
from batocera_launch import BatoceraException, Command, Emulator, HotkeysContext
from batocera_launch.paths import configure_emulator

from .controllers import generate_controllers_config
from .sfo import SFO

if TYPE_CHECKING:
    from types import TracebackType

_logger = logging.getLogger(__name__)

_BIN_PATH: Final = Path('/usr/bin/rpcs3')
_OVERCOMMIT_PATH: Final = Path('/proc/sys/vm/overcommit_memory')

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

# RPCS3 game patches required by the arcade titles, merged into the user's
# patches/imported_patch.yml. New PPU entries are added without overwriting any the
# user may already have.
_ARCADE_PATCHES: Final[dict[str, Any]] = {
    'Version': 1.2,
    'PPU-31faa92273d6269ea41b4d158e443f3d0e4174a7': {
        'Bypass Security Checks (Green)': {
            'Games': {'Taiko no Tatsujin': {'SCEEXE000': ['01.00']}},
            'Author': 'GetzeAve',
            'Notes': 'Yes.',
            'Patch Version': 1.0,
            'Patch': [['be32', '0x004b69e8', '0x38600000']],
        },
    },
    'PPU-17fe05b18e1e6b40d5387418529be44fdf5e39a3': {
        'Bypass Security Checks (Wadaiko)': {
            'Games': {'Taiko no Tatsujin': {'SCEEXE000': ['01.00']}},
            'Author': 'GetzeAve',
            'Notes': 'Yes.',
            'Patch Version': 1.0,
            'Patch': [['be32', '0x00347060', '0x38600000']],
        },
    },
    'PPU-d3af4341bb24860b223158db5b0093c87bf91d90': {
        'Bypass Security Checks (Momoiro)': {
            'Games': {'Taiko no Tatsujin': {'SCEEXE000': ['01.00']}},
            'Author': 'GetzeAve',
            'Notes': 'Yes.',
            'Patch Version': 1.0,
            'Patch': [['be32', '0x0032d910', '0x38600000']],
        },
    },
    'PPU-f20ba6cf299b3873d7007f8a4f1e8efd2319ade4': {
        'Bypass Security Checks (Murasaki)': {
            'Games': {'Taiko no Tatsujin': {'SCEEXE000': ['01.00']}},
            'Author': 'GetzeAve',
            'Notes': 'Yes.',
            'Patch Version': 1.0,
            'Patch': [['be32', '0x0039d238', '0x38600000']],
        },
    },
    'PPU-2e6b644196e1fa089efd4d87db9c43fe81e81263': {
        'Bypass Security Checks (Red)': {
            'Games': {'Taiko no Tatsujin': {'SCEEXE000': ['01.00']}},
            'Author': 'GetzeAve',
            'Notes': 'Yes.',
            'Patch Version': 1.0,
            'Patch': [['be32', '0x0041ec50', '0x38600000']],
        },
    },
    'PPU-58f3c6e971e82e67b0c69cfdd362e0ca60ce92a4': {
        'Bypass Security Checks (White)': {
            'Games': {'Taiko no Tatsujin': {'SCEEXE000': ['01.00']}},
            'Author': 'GetzeAve',
            'Notes': 'Yes.',
            'Patch Version': 1.0,
            'Patch': [['be32', '0x0041f738', '0x38600000']],
        },
    },
    'PPU-de4bd316b3e0a94b1620dc0b8c663f3ff865f409': {
        'Bypass Security Checks (Yellow)': {
            'Games': {'Taiko no Tatsujin': {'SCEEXE000': ['01.00']}},
            'Author': 'GetzeAve',
            'Notes': 'Yes.',
            'Patch Version': 1.0,
            'Patch': [['be32', '0x00456638', '0x38600000']],
        },
    },
    'PPU-0ac0a218b038d56c015bc33018f2875d406547e8': {
        'Bypass Security Checks (Blue)': {
            'Games': {'Taiko no Tatsujin': {'SCEEXE000': ['01.00']}},
            'Author': 'GetzeAve',
            'Notes': 'Yes.',
            'Patch Version': 1.0,
            'Patch': [['be32', '0x00474b78', '0x38600000']],
        },
    },
    'PPU-0b8c2d5f0d1819cdaafaa297da508065b7b00edb': {
        'Bypass Security Checks (Kimidori)': {
            'Games': {'Taiko no Tatsujin': {'SCEEXE000': ['01.00']}},
            'Author': 'GetzeAve',
            'Notes': 'Yes.',
            'Patch Version': 1.0,
            'Patch': [['be32', '0x0035b4c8', '0x38600000']],
        },
    },
    'PPU-78cfd074e799c0aeaf5e4241c597f741ba10bd1a': {
        'Bypass Security Checks (KATSU-DON)': {
            'Games': {'Taiko no Tatsujin': {'SCEEXE000': ['01.00']}},
            'Author': 'GetzeAve',
            'Notes': 'Yes.',
            'Patch Version': 1.0,
            'Patch': [['be32', '0x00299e10', '0x38600000']],
        },
    },
    'PPU-38935c6c0a4cc67b8908ed312fafaa8a605a18e4': {
        'Bypass Security Checks (Sorairo)': {
            'Games': {'Taiko no Tatsujin': {'SCEEXE000': ['01.00']}},
            'Author': 'GetzeAve',
            'Notes': 'Yes.',
            'Patch Version': 1.0,
            'Patch': [['be32', '0x002d5098', '0x38600000']],
        },
    },
}

# Patch enable state required by the Taiko titles, merged into patches/patch_config.yml.
_TAIKO_PATCH_CONFIG: Final[dict[str, Any]] = {
    'PPU-38935c6c0a4cc67b8908ed312fafaa8a605a18e4': {
        'Bypass Security Checks (Sorairo)': {
            'Taiko no Tatsujin': {'SCEEXE000': {'01.00': {'Enabled': True}}},
        },
    },
    'PPU-78cfd074e799c0aeaf5e4241c597f741ba10bd1a': {
        'Bypass Security Checks (KATSU-DON)': {
            'Taiko no Tatsujin': {'SCEEXE000': {'01.00': {'Enabled': True}}},
        },
    },
    'PPU-2e6b644196e1fa089efd4d87db9c43fe81e81263': {
        'Bypass Security Checks (Red)': {
            'Taiko no Tatsujin': {'SCEEXE000': {'01.00': {'Enabled': True}}},
        },
    },
    'PPU-d3af4341bb24860b223158db5b0093c87bf91d90': {
        'Bypass Security Checks (Momoiro)': {
            'Taiko no Tatsujin': {'SCEEXE000': {'01.00': {'Enabled': True}}},
        },
    },
    'PPU-17fe05b18e1e6b40d5387418529be44fdf5e39a3': {
        'Bypass Security Checks (Wadaiko)': {
            'Taiko no Tatsujin': {'SCEEXE000': {'01.00': {'Enabled': True}}},
        },
    },
    'PPU-31faa92273d6269ea41b4d158e443f3d0e4174a7': {
        'Bypass Security Checks (Green)': {
            'Taiko no Tatsujin': {'SCEEXE000': {'01.00': {'Enabled': True}}},
        },
    },
    'PPU-f20ba6cf299b3873d7007f8a4f1e8efd2319ade4': {
        'Bypass Security Checks (Murasaki)': {
            'Taiko no Tatsujin': {'SCEEXE000': {'01.00': {'Enabled': True}}},
        },
    },
    'PPU-de4bd316b3e0a94b1620dc0b8c663f3ff865f409': {
        'Bypass Security Checks (Yellow)': {
            'Taiko no Tatsujin': {'SCEEXE000': {'01.00': {'Enabled': True}}},
        },
    },
    'PPU-0ac0a218b038d56c015bc33018f2875d406547e8': {
        'Bypass Security Checks (Blue)': {
            'Taiko no Tatsujin': {'SCEEXE000': {'01.00': {'Enabled': True}}},
        },
    },
    'PPU-58f3c6e971e82e67b0c69cfdd362e0ca60ce92a4': {
        'Bypass Security Checks (White)': {
            'Taiko no Tatsujin': {'SCEEXE000': {'01.00': {'Enabled': True}}},
        },
    },
    'PPU-0b8c2d5f0d1819cdaafaa297da508065b7b00edb': {
        'Bypass Security Checks (Kimidori)': {
            'Taiko no Tatsujin': {'SCEEXE000': {'01.00': {'Enabled': True}}},
        },
    },
}

# USIO emulated arcade I/O board button mapping (Taiko / Tekken / card reader), written
# verbatim as the global usio.yml for arcade titles.
_USIO_CONFIG: Final = """\
Player 1:
  Test: R3
  Coin: Select
  Service: L3
  Enter/Start: Start
  Up: D-Pad Up
  Down: D-Pad Down
  Left: D-Pad Left
  Right: D-Pad Right
  Taiko Hit Side Left: Square
  Taiko Hit Side Right: Circle
  Taiko Hit Center Left: Triangle
  Taiko Hit Center Right: Cross
  Tekken Button 1: Square
  Tekken Button 2: Triangle
  Tekken Button 3: Cross
  Tekken Button 4: Circle
  Tekken Button 5: R1
  Card Tapping: L1
Player 2:
  Test: R3
  Coin: Select
  Service: L3
  Enter/Start: Start
  Up: D-Pad Up
  Down: D-Pad Down
  Left: D-Pad Left
  Right: D-Pad Right
  Taiko Hit Side Left: Square
  Taiko Hit Side Right: Circle
  Taiko Hit Center Left: Triangle
  Taiko Hit Center Right: Cross
  Tekken Button 1: Square
  Tekken Button 2: Triangle
  Tekken Button 3: Cross
  Tekken Button 4: Circle
  Tekken Button 5: R1
  Card Tapping: L1
Player 3:
  Test: Select
  Coin: L3
  Service: R3
  Enter/Start: Start
  Up: D-Pad Up
  Down: D-Pad Down
  Left: D-Pad Left
  Right: D-Pad Right
  Taiko Hit Side Left: Square
  Taiko Hit Side Right: Circle
  Taiko Hit Center Left: Triangle
  Taiko Hit Center Right: Cross
  Tekken Button 1: Square
  Tekken Button 2: Triangle
  Tekken Button 3: Cross
  Tekken Button 4: Circle
  Tekken Button 5: R1
  Card Tapping: L1
Player 4:
  Test: Select
  Coin: L3
  Service: R3
  Enter/Start: Start
  Up: D-Pad Up
  Down: D-Pad Down
  Left: D-Pad Left
  Right: D-Pad Right
  Taiko Hit Side Left: Square
  Taiko Hit Side Right: Circle
  Taiko Hit Center Left: Triangle
  Taiko Hit Center Right: Cross
  Tekken Button 1: Square
  Tekken Button 2: Triangle
  Tekken Button 3: Cross
  Tekken Button 4: Circle
  Tekken Button 5: R1
  Card Tapping: L1
"""


def _get_firmware_version(config_dir: Path, /) -> str | None:
    try:
        with (config_dir / 'dev_flash' / 'vsh' / 'etc' / 'version.txt').open('r') as stream:
            lines = stream.readlines()
        for line in lines:
            matches = re.match('^release:(.*):', line)
            if matches:
                return matches[1]
    except Exception:
        return None
    return None


def _migrate_dev_hdd0(config_dir: Path, hdd0_dir: Path, /) -> None:
    legacy_dev_hdd0 = config_dir / 'dev_hdd0'
    if not legacy_dev_hdd0.exists():
        # New install or fully migrated: nothing to do
        return

    if hdd0_dir.exists():
        # Partial or failed migration: leave it alone
        _logger.warning('Skipping RPCS3 dev_hdd0 migration: target directory already exists at %s', hdd0_dir)
        return

    hdd0_dir.parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.copytree(legacy_dev_hdd0, hdd0_dir)
    except Exception:
        _logger.exception('Failed to copy RPCS3 dev_hdd0 from %s to %s', legacy_dev_hdd0, hdd0_dir)
        return

    _logger.debug('Successfully copied RPCS3 dev_hdd0 from %s to %s', legacy_dev_hdd0, hdd0_dir)

    differences = directory_differences(legacy_dev_hdd0, hdd0_dir)
    if differences:
        _logger.error('RPCS3 dev_hdd0 migration verification failed:\n%s', differences.report())
        return

    _logger.debug('Verified RPCS3 dev_hdd0 migration from %s to %s', legacy_dev_hdd0, hdd0_dir)

    shutil.rmtree(legacy_dev_hdd0)

    _logger.debug('Completed RPCS3 dev_hdd0 migration from %s to %s', legacy_dev_hdd0, hdd0_dir)


def _deep_merge_missing(destination: dict[str, Any], source: Mapping[str, Any], /) -> bool:
    changed = False

    for key, value in source.items():
        if key not in destination:
            destination[key] = value
            changed = True

        elif isinstance(destination[key], dict) and isinstance(value, Mapping):
            changed |= _deep_merge_missing(destination[key], cast('Mapping[str, Any]', value))

    return changed


def _merge_patch_config(config_file: Path, data: Mapping[str, Any], /) -> None:
    # Create the target patch file from data if absent, otherwise merge in only the keys
    # not yet present (preserving the user's own patches and enable/disable state).

    yaml = YAML()  # round-trip: preserve the user's file formatting and the hex literals

    config_file.parent.mkdir(parents=True, exist_ok=True)

    if not config_file.is_file():
        yaml.dump(data, config_file)  # pyright: ignore
        return

    with config_file.open() as f:
        existing = cast('dict[str, Any]', yaml.load(f) or {})  # pyright: ignore

    if _deep_merge_missing(existing, data):
        yaml.dump(existing, config_file)  # pyright: ignore


async def _fetch_compatibility_database(target_path: Path, /) -> None:
    """Download RPCS3 compatibility database to /tmp/rpcs3, compare, and update if changed."""
    tmp_dir = Path('/tmp/rpcs3')
    tmp_file = tmp_dir / target_path.name

    try:
        tmp_dir.mkdir(parents=True, exist_ok=True)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        async with (
            aiohttp.ClientSession() as session,
            session.get(
                'https://api.rpcs3.net/config/?api=v1',
                headers={'User-Agent': 'RPCS3/Batocera'},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as response,
        ):
            tmp_file.write_bytes(await response.read())

        # If destination doesn't exist or content has changed, overwrite it
        if not target_path.exists() or not filecmp.cmp(tmp_file, target_path, shallow=False):
            shutil.move(tmp_file, target_path)
            _logger.debug('Updated RPCS3 compatibility database at %s', target_path)
        else:
            _logger.debug('RPCS3 compatibility database is already up to date')
            tmp_file.unlink(missing_ok=True)

    except Exception as e:
        _logger.debug('Could not update RPCS3 compatibility database: %s', e)
        if tmp_file.exists():
            try:
                tmp_file.unlink()
            except OSError:
                pass


@dataclass(slots=True)
class RPCS3Command(Command):
    async def run(self) -> int:
        original_overcommit: str | None = None

        try:
            original_overcommit = _OVERCOMMIT_PATH.read_text()
            _OVERCOMMIT_PATH.write_text('1\n')
        except Exception:
            _logger.warning('Failed to set vm.overcommit_memory=1', exc_info=True)

        try:
            return await super().run()
        finally:
            if original_overcommit is not None:
                try:
                    _OVERCOMMIT_PATH.write_text(original_overcommit)
                except Exception:
                    _logger.warning('Failed to restore vm.overcommit_memory', exc_info=True)


@cached_dataclass
class RPCS3(Emulator):
    compatibility_database_task: asyncio.Task[None] = field(init=False)

    async def __aenter__(self) -> Self:
        # Start downloading the compatibility database ASAP in the background
        self.compatibility_database_task = asyncio.create_task(
            _fetch_compatibility_database(self.config_dir / 'GuiConfigs' / 'config_database.dat')
        )

        try:
            return await super().__aenter__()
        except BaseException:
            # Cancel the task if the context manager fails to enter (e.g. KeyboardInterrupt)
            self.compatibility_database_task.cancel()
            try:
                # await the task and suppress the CancelledError to ensure aiohttp cleanup happens
                await self.compatibility_database_task
            except asyncio.CancelledError:
                pass

            raise

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> bool | None:
        # Cancel the task if the context manager exits
        self.compatibility_database_task.cancel()
        try:
            # await the task and suppress the CancelledError to ensure aiohttp cleanup happens
            await self.compatibility_database_task
        except asyncio.CancelledError:
            pass

        return await super().__aexit__(exc_type, exc_value, traceback)

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'rpcs3',
            'keys': {
                'exit': '/usr/bin/rpcs3-exit',
                'menu': ['KEY_LEFTSHIFT', 'KEY_F10'],
                'pause': ['KEY_LEFTCTRL', 'KEY_P'],
            },
        }

    @cached_property
    def hdd0_dir(self) -> Path:
        return self.saves_dir / 'rpcs3' / 'dev_hdd0'

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    @property
    def needs_overlayfs(self) -> bool:
        return True

    @property
    def closest_screen_ratio(self) -> str:
        screen_ratio = self.resolution.width / self.resolution.height
        return '4:3' if screen_ratio < 1.6 else '16:9'

    @cached_property
    def rom_dev_hdd0(self) -> Path:
        return self.rom / 'dev_hdd0'

    @cached_property
    def rom_dev_hdd1(self) -> Path:
        return self.rom / 'dev_hdd1'

    @cached_property
    def rom_game_dir(self) -> Path:
        return self.rom_dev_hdd0 / 'game'

    @cached_property
    def is_psn_squashfs(self) -> bool:
        # Detect PSN game packed as a squashfs: emulatorlauncher has already mounted the
        # squashfs and (via writesToRom=True) created a writable overlayfs, so rom is
        # /var/run/overlays/<stem> mirroring the dev_hdd0 layout.
        return self.rom.is_dir() and str(self.rom).startswith('/var/run/') and self.rom_game_dir.is_dir()

    @cached_property
    def arcade_game_title(self) -> str | None:
        # Match an arcade PSN squashfs title via its PARAM.SFO TITLE (a key of _ARCADE_USB_CONFIG).
        # Arcade titles all ship under the same SCEEXE000 title-id.
        if not self.is_psn_squashfs:
            return None

        if (sfo_file := self.rom_game_dir / 'SCEEXE000' / 'PARAM.SFO').is_file():
            sfo = SFO.from_path(sfo_file)
            title = sfo.TITLE

            if title and title in _ARCADE_USB_CONFIG:
                _logger.debug("Matched RPCS3 arcade title '%s'", title)
                return title

        return None

    def _generate_vfs_config(self, /) -> None:
        arcade_usb_config = _ARCADE_USB_CONFIG.get(self.arcade_game_title or '', {})

        dev_hdd0 = f'{self.rom_dev_hdd0 if self.is_psn_squashfs else self.hdd0_dir}/'
        # For a PSN squashfs, redirect /dev_hdd1/ to the overlay when it ships one.
        dev_hdd1 = (
            f'{self.rom_dev_hdd1 if self.is_psn_squashfs and self.rom_dev_hdd1.is_dir() else "$(EmulatorDir)dev_hdd1"}/'
        )

        # Build the full /dev_usb***/ block (slots 000-007). Every tuned slot (one carrying
        # an emulated USB I/O board Serial/VID/PID) reads its data from the overlay's single
        # dev_usb000 folder, so its Path defaults there; a slot may override "Path" (e.g. ""
        # for a pure passthrough device). Untuned dev_usb000 keeps the RPCS3 default mount
        # (or the overlay folder if shipped) and the rest stay empty.
        overlay_usb000_dir = self.rom / 'dev_usb000'
        overlay_usb000 = f'{overlay_usb000_dir}/'

        if arcade_usb_config and self.is_psn_squashfs:
            overlay_usb000_dir.mkdir(parents=True, exist_ok=True)

        usb_config: dict[str, dict[str, str]] = {}

        for index in range(8):
            slot = f'/dev_usb00{index}'
            slot_usb_config = arcade_usb_config.get(slot, {})
            usb_dir = self.rom / f'dev_usb00{index}'

            if slot_usb_config:
                path = slot_usb_config.get('Path', overlay_usb000 if self.is_psn_squashfs else '')
            elif self.is_psn_squashfs and usb_dir.is_dir():
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
            self.config_dir / 'vfs.yml',
        )

    def _generate_patch_config(self, /) -> None:
        # arcade titles need their game patches imported and the USIO board input mapping;
        # Taiko titles also need the matching patch enable state

        if self.arcade_game_title:
            _merge_patch_config(self.config_dir / 'patches' / 'imported_patch.yml', _ARCADE_PATCHES)
            (self.config_dir / 'usio.yml').write_text(_USIO_CONFIG, encoding='utf-8')

            if self.arcade_game_title.startswith('Taiko no Tatsujin'):
                _merge_patch_config(self.config_dir / 'patch_config.yml', _TAIKO_PATCH_CONFIG)

    async def configure(self) -> Command:
        _migrate_dev_hdd0(self.config_dir, self.hdd0_dir)

        self.hdd0_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        generate_controllers_config(
            self.config_dir, self.config, self.controllers, keyboard=bool(self.arcade_game_title)
        )

        # Taking care of the CurrentSettings.ini file
        current_settings_path = self.config_dir / 'GuiConfigs' / 'CurrentSettings.ini'
        current_settings_path.parent.mkdir(parents=True, exist_ok=True)

        # Generates CurrentSettings.ini with values to disable prompts on first run
        current_settings = CaseSensitiveConfigParser(interpolation=None)
        if current_settings_path.exists():
            current_settings.read(current_settings_path)

        # Sets Gui Settings to close completely and disables some popups
        if not current_settings.has_section('main_window'):
            current_settings.add_section('main_window')

        current_settings.set('main_window', 'confirmationBoxExitGame', 'false')
        current_settings.set('main_window', 'infoBoxEnabledInstallPUP', 'false')
        current_settings.set('main_window', 'infoBoxEnabledWelcome', 'false')

        with current_settings_path.open('w') as configfile:
            current_settings.write(configfile)

        config_file_path = self.config_dir / 'config.yml'

        # Generate a default config if it doesn't exist otherwise just open the existing
        rpcs3_yml_config: dict[str, dict[str, Any]] = {}
        if config_file_path.is_file():
            rpcs3_yml_config = safe_load_yaml12(config_file_path, dict[str, dict[str, Any]]) or {}

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

        vulkan_info = await vulkan.get_vulkan_info()
        backend = self.config.get('rpcs3_gfxbackend', 'Vulkan') if vulkan_info else 'OpenGL'

        if vulkan_info:
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
            case (
                'Off'
                | '30'
                | '50'
                | '59.94'
                | '60'
                | '120'
                | 'Display'
                | 'Auto'
                | 'PS3 Native'
                | 'Infinite' as rpcs3_framelimit
            ):
                frame_limit = rpcs3_framelimit
                second_frame_limit = 0
            case _ as rpcs3_framelimit:
                try:
                    frame_limit = 'Off'
                    second_frame_limit = float(rpcs3_framelimit)
                except Exception:
                    frame_limit = 'Auto'
                    second_frame_limit = 0

        match self.config.get('rpcs3_zcull'):
            case 'Approximate':
                accurate_zcull_stats = False
                relaxed_zcull_sync = False
                disable_zcull_occlusion_queries = False
            case 'Relaxed':
                accurate_zcull_stats = False
                relaxed_zcull_sync = True
                disable_zcull_occlusion_queries = False
            case 'Disable':
                accurate_zcull_stats = False
                relaxed_zcull_sync = False
                disable_zcull_occlusion_queries = True
            case _:
                accurate_zcull_stats = True
                relaxed_zcull_sync = False
                disable_zcull_occlusion_queries = False

        time_stretch = self.config.get_bool('rpcs3_timestretch')

        config: dict[str, Any] = {
            'Core': {
                # Set the PPU Decoder based on config
                'PPU Decoder': self.config.get('rpcs3_ppudecoder', 'Recompiler (LLVM)'),
                # Set the SPU Decoder based on config
                'SPU Decoder': self.config.get('rpcs3_spudecoder', 'Recompiler (LLVM)'),
                # Set the SPU XFloat Accuracy based on config
                'SPU XFloat Accuracy': self.config.get('rpcs3_spuxfloataccuracy', 'Approximate'),
                # Force to True for now to account for updates where exiting config file present. (True results in less stutter when a SPU module is in cache)
                'SPU Cache': True,
                # Preferred SPU Threads
                'Preferred SPU Threads': self.config.get_int('rpcs3_sputhreads', 0),
                # SPU Loop Detection
                'SPU loop detection': self.config.get_bool('rpcs3_spuloopdetection'),
                # SPU Block Size
                'SPU Block Size': self.config.get('rpcs3_spublocksize', 'Safe'),
                # Thread Scheduler Mode
                'Thread Scheduler Mode': self.config.get('rpcs3_thread_scheduler', 'Operating System'),
                # Clocks scale
                'Clocks scale': self.config.get_int('rpcs3_clocks_scale', 100),
                # Max Power Saving CPU-Preemptions
                # values are maximum yields per frame threshold
                'Max CPU Preempt Count': self.config.get_int('rpcs3_maxcpu_preemptcount', 0),
                # Sleep Timers Accuracy
                'Sleep Timers Accuracy': self.config.get('rpcs3_sleep_timers_accuracy', 'As Host'),
                # RSX FIFO Fetch Accuracy
                'RSX FIFO Fetch Accuracy': self.config.get('rpcs3_rsx_fifo', 'Atomic'),
            },
            'Video': {
                'Renderer': backend,
                # System aspect ratio (the setting in the PS3 system itself, not the displayed ratio) a.k.a. TV mode.
                # If not set, see if the screen ratio is closer to 4:3 or 16:9 and pick that.
                'Aspect ratio': self.config.get('rpcs3_ratio') or self.closest_screen_ratio,
                # Shader compilation
                'Shader Mode': self.config.get('rpcs3_shadermode', 'Async with Shader Interpreter'),
                # Vsync
                'VSync Mode': self.config.get('rpcs3_vsync', 'Disabled'),
                # Stretch to display area
                'Stretch To Display Area': self.config.get_bool('rpcs3_stretchdisplay'),
                # Frame Limit
                # Frame limit checks for specific values("Auto", "Off", "30", "50", "59.94", "60", "120", "Display", "PS3 Native", "Infinite")
                # Second Frame Limit can be any float/integer. 0 = disabled.
                'Frame limit': frame_limit,
                'Second Frame Limit': second_frame_limit,
                # Write Color Buffers
                'Write Color Buffers': self.config.get_bool('rpcs3_colorbuffers')
                or self.arcade_game_title == 'Deadstorm Pirates Special Edition',
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
                'Disable ZCull Occlusion Queries': disable_zcull_occlusion_queries,
                # Shader Precision
                'Shader Precision': self.config.get('rpcs3_shader', 'Auto'),
                # Internal resolution (CHANGE AT YOUR OWN RISK)
                'Resolution': '1280x720',
                # Resolution scaling
                'Resolution Scale': self.config.get_int('rpcs3_resolution_scale', 100),
                # Resolution scale threshold
                'Minimum Scalable Dimension': int(self.config.get_float('rpcs3_resolution_scale_threshold', 16)),
                # Output Scaling
                'Output Scaling Mode': self.config.get('rpcs3_scaling', 'Bilinear'),
                # CAS Sharpening
                'FidelityFX CAS Sharpening Intensity': self.config.get_int('rpcs3_fsr_sharpening', 50),
                # Number of Shader Compilers
                'Shader Compiler Threads': self.config.get_int('rpcs3_num_compilers', 0),
                # Multithreaded RSX
                'Multithreaded RSX': self.config.get_bool('rpcs3_rsx'),
                # Write Depth Buffer
                'Write Depth Buffer': self.config.get_bool('rpcs3_write_depth_buffers'),
                # Read Depth Buffer
                'Read Depth Buffer': self.config.get_bool('rpcs3_read_depth_buffers'),
                # Strict Rendering Mode
                'Strict Rendering Mode': self.config.get_bool('rpcs3_strict'),
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
                'Desired Audio Buffer Duration': self.config.get_int('rpcs3_audiobuffer_duration', 34),
                # time stretching
                'Enable Time Stretching': time_stretch,
                'Time Stretching Threshold': self.config.get_int('rpcs3_timestretch_threshold', 75),
            },
            'Input/Output': {
                'Pad handler mode': self.config.get('rpcs3_pad_mode', 'Single-threaded'),
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
            assert vulkan_info is not None

            vulkan_config = config['Video']['Vulkan'] = {}

            if discrete_gpu := vulkan_info.active_discrete_gpu:
                _logger.debug('A discrete GPU is available on the system. We will use that for performance')
                discrete_name = discrete_gpu.name
                if discrete_name:
                    _logger.debug('Using Discrete GPU Name: %s for RPCS3', discrete_name)
                    vulkan_config['Adapter'] = discrete_name
                else:
                    _logger.debug("Couldn't get discrete GPU Name")
            else:
                _logger.debug('Discrete GPU is not available on the system. Using default.')

            vulkan_config['Asynchronous Texture Streaming'] = self.config.get_bool('rpcs3_async_texture')
            # Asynchronous Queue Scheduler
            if self.config.get('rpcs3_vk_async_scheduler'):
                vulkan_config['Asynchronous Queue Scheduler'] = self.config.get('rpcs3_vk_async_scheduler')

        merge(rpcs3_yml_config, config)

        if self.arcade_game_title:
            rpcs3_yml_config['System']['Console PSID'] = 0
        else:
            rpcs3_yml_config['System'].pop('Console PSID', None)

        # Clear leftover gun settings from a previous run when no gun is present
        if not (self.config.use_guns and self.guns) and rpcs3_yml_config.get('Input/Output', {}).get('Move') == 'Gun':
            rpcs3_yml_config['Input/Output']['Move'] = 'Null'
            rpcs3_yml_config['Input/Output']['Camera'] = 'Null'
            rpcs3_yml_config['Input/Output']['Camera type'] = 'Unknown'

        rpcs3_yml_config['Video'].pop('VSync', None)

        if 'Vulkan' in rpcs3_yml_config['Video']:
            rpcs3_yml_config['Video']['Vulkan'].pop('Asynchronous Texture Streaming 2', None)

        safe_dump_yaml12(rpcs3_yml_config, config_file_path)

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
                self.config_dir / 'gem_gun.yml',
            )

        self._generate_vfs_config()
        self._generate_patch_config()

        # copy icon files to config
        icon_target = self.config_dir / 'Icons'
        icon_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree('/usr/share/rpcs3/Icons/', icon_target, dirs_exist_ok=True, copy_function=shutil.copy2)

        # determine the rom name
        rom_name: Path | None = None

        if self.rom.suffix == '.psn':
            with self.rom.open() as fp:
                for line in fp:
                    if len(line) >= 9:
                        rom_name = self.hdd0_dir / 'game' / line.strip().upper() / 'USRDIR' / 'EBOOT.BIN'

            if rom_name is None:
                raise BatoceraException(f'No game ID found in {self.rom}')

        elif self.is_psn_squashfs:
            # rom is /var/run/overlays/<stem>; dev_hdd0 is redirected there via vfs.yml.
            # Scan for the game ID directory and pass EBOOT.BIN directly to RPCS3.
            for game_id_dir in self.rom_game_dir.iterdir():
                eboot = game_id_dir / 'USRDIR' / 'EBOOT.BIN'
                if eboot.exists():
                    rom_name = eboot
                    break

            if rom_name is None:
                raise BatoceraException(f'No PSN game found in squashfs {self.rom}')

        elif self.rom.suffix.lower() == '.iso':
            rom_name = self.rom
        elif not configure_emulator(self.rom):
            rom_name = self.rom / 'PS3_GAME' / 'USRDIR' / 'EBOOT.BIN'

        args: list[Path | str] = [_BIN_PATH, rom_name] if rom_name else [_BIN_PATH]

        if not self.config.get_bool('rpcs3_gui') and rom_name:
            args.append('--no-gui')

        # firmware not installed and available : instead of starting the game, install it
        if _get_firmware_version(self.config_dir) is None and (BIOS / 'PS3UPDAT.PUP').exists():
            args = [_BIN_PATH, '--installfw', BIOS / 'PS3UPDAT.PUP']

        return RPCS3Command(
            args,
            {
                'XDG_CONFIG_HOME': CONFIGS,
                'XDG_CACHE_HOME': CACHE,
                'LC_ALL': 'C',
            },
            # Wait for the compatibility database update to finish (or fail) before running the command
            self.compatibility_database_task,
        )
