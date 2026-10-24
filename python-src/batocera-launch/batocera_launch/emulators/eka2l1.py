# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

from __future__ import annotations

import json
import logging
import shutil
import zipfile
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, Final, NamedTuple, cast

import ruamel.yaml

from batocera_common.configparser import CaseSensitiveRawConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CACHE, CONFIGS, ROMS, SAVES
from batocera_launch import BatoceraException, Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

_logger = logging.getLogger(__name__)

_BINARY: Final = Path('/usr/eka2l1/eka2l1_qt')

# EKA2L1 resolves $XDG_DATA_HOME/EKA2L1 for its config.yml, bindings/ and compat/ files, and
# changes into it at startup, so relative paths in its config are relative to this folder.
_HOME: Final = CONFIGS / 'EKA2L1'
_DEFAULT_STORAGE: Final = SAVES / 'eka2l1'

# The interface settings, a QSettings file under $XDG_CONFIG_HOME, which ends up in the same folder
_QT_SETTINGS: Final = _HOME / 'EKA2L1.conf'
# QColor(Qt::black) the way QSettings serializes it; a plain color name is not read back
_BLACK_QCOLOR: Final = r'@Variant(\0\0\0\x43\x1\xff\xff\0\0\0\0\0\0\0\0)'

# The Android and Windows builds keep everything in one portable EKA2L1 folder, which people
# often put next to their games and share between devices: data/ holds the installed devices,
# drives and saves, compat/ the per-game settings. Both are used as they are when found here.
_PORTABLE_ROOTS: Final = (ROMS / 'ngage' / 'EKA2L1', ROMS / 'symbian' / 'EKA2L1')

# N-Gage QD first: same games, and the dump that most people have.
_NGAGE_DEVICES: Final = ('RH-29', 'NEM-4')

# Symbian OS versions on the EKA1 kernel, what the pre-9.x SIS format targets (S60v1/v2, UIQ 2).
_EKA1_PLATFORMS: Final = frozenset({'epocu6', 'epoc6', 'epoc70', 'epoc7', 'epoc80', 'epoc81a'})

_SISX_UID1: Final = 0x10201A7A
_SIS_UID2: Final = 0x1000006D
_SIS_UID3: Final = 0x10000419


class Device(NamedTuple):
    firmware_code: str
    platform: str

    @property
    def is_eka1(self) -> bool:
        return self.platform in _EKA1_PLATFORMS


class LaunchInfo(NamedTuple):
    uid: int
    device: str | None


class SisInfo(NamedTuple):
    uid: int
    is_sisx: bool


class Launch(NamedTuple):
    args: list[str | Path]
    # UIDs of the applications the game may run, for the per-game settings
    app_uids: list[int]


def _portable_root(roots: Iterable[Path] = _PORTABLE_ROOTS, /) -> Path | None:
    return next((root for root in roots if (root / 'data' / 'devices.yml').is_file()), None)


def _installed_devices(storage: Path, /) -> list[Device]:
    devices_file = storage / 'devices.yml'
    if not devices_file.is_file():
        return []

    with devices_file.open() as fp:
        devices = cast('Mapping[str, Mapping[str, Any]] | None', ruamel.yaml.YAML(typ='safe').load(fp))  # pyright: ignore

    return [
        Device(str(device.get('firmcode', code)), str(device.get('platver', '')))
        for code, device in (devices or {}).items()
    ]


def _find_device(devices: Iterable[Device], firmware_code: str, /) -> Device | None:
    return next((device for device in devices if device.firmware_code.lower() == firmware_code.lower()), None)


def _parse_uid(value: object, /) -> int:
    if isinstance(value, bool):
        raise ValueError(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value.strip(), 0)

    raise ValueError(value)


def _read_launch_info(path: Path, /) -> LaunchInfo:
    """Read an EKA2L1 shortcut, the JSON file the Android build exports for frontends."""
    try:
        info = cast('dict[str, object]', json.loads(path.read_text(encoding='utf-8')))
        uid = _parse_uid(info['AppUid'])
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise BatoceraException(f'Not a valid EKA2L1 shortcut: {path.name}') from e

    device = info.get('DeviceCode')
    return LaunchInfo(uid, str(device) if device else None)


def _read_sis_info(path: Path, /) -> SisInfo:
    try:
        with path.open('rb') as fp:
            header = fp.read(12)
    except OSError as e:
        raise BatoceraException(f'Unable to read {path.name}') from e

    if len(header) == 12:
        uid1, uid2, uid3 = (int.from_bytes(header[i : i + 4], 'little') for i in (0, 4, 8))

        # Symbian 9.x: UID3 is the package UID, the same as the application's in practice
        if uid1 == _SISX_UID1:
            return SisInfo(uid3, True)
        # Older SIS: UID1 is the application UID
        if uid2 == _SIS_UID2 and uid3 == _SIS_UID3:
            return SisInfo(uid1, False)

    raise BatoceraException(f'Not a SIS package: {path.name}')


def _game_card_uids(path: Path, /) -> list[int]:
    """UIDs of the applications on an N-Gage game card dump, read from their .aif files inside the zip."""
    uids: list[int] = []

    try:
        with zipfile.ZipFile(path) as card:
            for entry in card.infolist():
                parts = PurePosixPath(entry.filename.lower()).parts
                # <...>/system/apps/<app>/<app>.aif
                if len(parts) < 4 or parts[-4:-2] != ('system', 'apps') or not parts[-1].endswith('.aif'):
                    continue

                header = card.read(entry)[:12]
                if len(header) == 12:
                    uids.append(int.from_bytes(header[8:12], 'little'))
    except OSError, zipfile.BadZipFile:
        _logger.debug('Unable to read the applications of %s', path, exc_info=True)

    return uids


def _pick_ngage_device(devices: list[Device], wanted: str, /) -> Device:
    for code in (wanted,) if wanted != 'auto' else _NGAGE_DEVICES:
        if device := _find_device(devices, code):
            return device

    raise BatoceraException(
        f'No N-Gage device installed in EKA2L1 ({" or ".join(_NGAGE_DEVICES) if wanted == "auto" else wanted})'
    )


def _pick_sis_device(devices: list[Device], sis: SisInfo, /) -> Device:
    # Packages built for Symbian 9 need an EKA2 device, older ones an EKA1 device
    if device := next((device for device in devices if device.is_eka1 != sis.is_sisx), None):
        return device

    raise BatoceraException(
        'No Symbian 9 (S60v3 or newer) device installed in EKA2L1'
        if sis.is_sisx
        else 'No Symbian 6-8 (S60v1/v2, N-Gage) device installed in EKA2L1'
    )


def _is_package_installed(storage: Path, device: Device, uid: int, /) -> bool:
    # EKA2L1 registers every package it installs in C:\sys\install\sisregistry\<uid>, drive C
    # being shared by all devices unless the device was installed with its own drives
    return any(
        (drives / 'c' / 'sys' / 'install' / 'sisregistry' / f'{uid:08x}').is_dir()
        for drives in (storage / 'drives', storage / 'drives' / device.firmware_code.lower())
    )


def _link_compat(home: Path, portable_compat: Path, /) -> None:
    compat = home / 'compat'
    if compat.is_symlink():
        if compat.readlink() == portable_compat:
            return
        compat.unlink()
    elif compat.is_dir():
        # Usually the copy EKA2L1 made of the settings it ships, which the portable folder has as well
        backup = home / 'compat.batocera-backup'
        if backup.is_dir():
            shutil.rmtree(backup)
        compat.rename(backup)

    home.mkdir(parents=True, exist_ok=True)
    compat.symlink_to(portable_compat, target_is_directory=True)


def _data_storage(portable_root: Path | None, /) -> Path:
    return portable_root / 'data' if portable_root is not None else _DEFAULT_STORAGE


def _update_config(storage: Path, portable_root: Path | None, /, **values: object) -> None:
    config_file = _HOME / 'config.yml'

    yaml = ruamel.yaml.YAML()
    config: dict[str, Any] = {}
    if config_file.is_file():
        with config_file.open() as fp:
            config = cast('dict[str, Any] | None', yaml.load(fp)) or {}  # pyright: ignore

    config['data-storage'] = str(storage)
    config['stop-warn-touchscreen-disabled'] = True
    config.update({key.replace('_', '-'): value for key, value in values.items()})

    _HOME.mkdir(parents=True, exist_ok=True)
    with config_file.open('w') as fp:
        yaml.dump(config, fp)  # pyright: ignore

    # Black around the screen, instead of the light grey of a phone's casing
    qt_settings = CaseSensitiveRawConfigParser(strict=False)
    if _QT_SETTINGS.is_file():
        qt_settings.read(_QT_SETTINGS)
    if not qt_settings.has_section('General'):
        qt_settings.add_section('General')
    qt_settings.set('General', 'backgroundDisplayColor', _BLACK_QCOLOR)
    with _QT_SETTINGS.open('w') as fp:
        qt_settings.write(fp, space_around_delimiters=False)

    if portable_root is not None and (portable_root / 'compat').is_dir():
        _link_compat(_HOME, portable_root / 'compat')


def prepare_standalone() -> None:
    """Point EKA2L1 at the same data as the games, before starting its own interface (batocera-config-eka2l1)."""
    portable_root = _portable_root()
    storage = _data_storage(portable_root)
    storage.mkdir(parents=True, exist_ok=True)
    _update_config(storage, portable_root)


def _set_app_fps(compat: Path, uids: Iterable[int], fps: int, /) -> None:
    yaml = ruamel.yaml.YAML()
    compat.mkdir(parents=True, exist_ok=True)

    for uid in uids:
        setting_file = compat / f'{uid:08X}.yml'
        setting: dict[str, Any] = {}
        if setting_file.is_file():
            with setting_file.open() as fp:
                setting = cast('dict[str, Any] | None', yaml.load(fp)) or {}  # pyright: ignore

        if setting.get('fps') == fps:
            continue

        setting['fps'] = fps
        with setting_file.open('w') as fp:
            yaml.dump(setting, fp)  # pyright: ignore


@cached_dataclass
class Eka2l1(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'eka2l1',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @cached_property
    def config_dir(self) -> Path:
        return _HOME

    @cached_property
    def saves_dir(self) -> Path:
        return self.data_storage

    @cached_property
    def portable_root(self) -> Path | None:
        return _portable_root()

    @cached_property
    def data_storage(self) -> Path:
        return _data_storage(self.portable_root)

    @cached_property
    def in_game_ratio(self) -> float:
        # N-Gage and most S60 phones have a 176x208 portrait screen
        return 176 / 208

    def _write_config(self) -> None:
        values: dict[str, object] = {
            'enable_nearest_neighbor_filter': self.config.get_bool('eka2l1_nearest_filter', True),
            'integer_scaling': self.config.get_bool('eka2l1_integer_scaling', True),
            'rtos_level': self.config.get_str('eka2l1_rtos_level', 'mid'),
        }
        if (language := self.config.get_int('eka2l1_language')) is not None:
            values['language'] = language

        _update_config(self.data_storage, self.portable_root, **values)

    def _launch(self, devices: list[Device]) -> Launch:
        if self.rom.suffix.lower() == '.json':
            launch = _read_launch_info(self.rom)
            if launch.device is None:
                raise BatoceraException(f'No DeviceCode in {self.rom.name}')

            device = _find_device(devices, launch.device)
            if device is None:
                raise BatoceraException(f'Device {launch.device} is not installed in EKA2L1')

            return Launch(['--device', device.firmware_code, '--run', f'0x{launch.uid:08X}'], [launch.uid])

        if self.rom.suffix.lower() in ('.sis', '.sisx'):
            sis = _read_sis_info(self.rom)
            device = _pick_sis_device(devices, sis)
            args: list[str | Path] = ['--device', device.firmware_code]

            # Installed on first launch only, then run straight away like any other game
            if not _is_package_installed(self.data_storage, device, sis.uid):
                _logger.info('Installing %s on %s', self.rom.name, device.firmware_code)
                args += ['--install', self.rom]

            return Launch([*args, '--run', f'0x{sis.uid:08X}'], [sis.uid])

        # An N-Gage game card dump: a .zip with the card's System folder, that EKA2L1 mounts as drive E
        # and finds the game on by itself
        device = _pick_ngage_device(devices, self.config.get_str('eka2l1_ngage_device', 'auto'))
        return Launch(['--device', device.firmware_code, '--mount', self.rom, '--runng'], _game_card_uids(self.rom))

    async def configure(self) -> Command:
        self._write_config()

        devices = _installed_devices(self.data_storage)
        if not devices:
            raise BatoceraException(
                f'No device installed in EKA2L1 ({self.data_storage}): install one from the EKA2L1 application first'
            )

        launch = self._launch(devices)

        # Most games are tied to the screen refresh, which EKA2L1 caps at 60 fps by default
        if (fps := self.config.get_int('eka2l1_fps')) is not None:
            _set_app_fps(_HOME / 'compat', launch.app_uids, fps)

        return Command(
            [_BINARY, *launch.args, '--fullscreen'],
            env={
                'XDG_CONFIG_HOME': CONFIGS,
                'XDG_DATA_HOME': CONFIGS,
                'XDG_CACHE_HOME': CACHE,
                'SDL_JOYSTICK_HIDAPI': '0',
            },
        )
