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
import zipfile
from pathlib import Path

import pytest

from batocera_launch import BatoceraException
from batocera_launch.emulators.eka2l1 import (
    _HOME,
    Device,
    SisInfo,
    _game_card_uids,
    _installed_devices,
    _is_package_installed,
    _link_compat,
    _pick_ngage_device,
    _pick_sis_device,
    _portable_root,
    _read_launch_info,
    _read_sis_info,
    _set_app_fps,
    _update_config,
)

pytestmark = pytest.mark.usefixtures('fs')

_PORTABLE = Path('/userdata/roms/ngage/EKA2L1')

_DEVICES_YML = """\
NEM-4:
  platver: epoc6
  manufacturer: (c)NMP
  firmcode: NEM-4
  model: V 4.03
  machine-uid: 270502937
RM-409:
  platver: epoc93fp2
  manufacturer: (c)Nokia
  firmcode: RM-409
  model: Nokia 5320d-1 (05.01)
  machine-uid: 536926810"""

_NGAGE = Device('NEM-4', 'epoc6')
_S60V3 = Device('RM-409', 'epoc93fp2')


def _write(path: Path, content: str | bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content)
    return path


def _uids(*uids: int) -> bytes:
    return b''.join(uid.to_bytes(4, 'little') for uid in uids)


class TestPortableRoot:
    def test_found_when_it_has_devices(self) -> None:
        _write(_PORTABLE / 'data' / 'devices.yml', _DEVICES_YML)

        assert _portable_root((Path('/userdata/roms/symbian/EKA2L1'), _PORTABLE)) == _PORTABLE

    def test_ignored_without_devices(self) -> None:
        (_PORTABLE / 'data').mkdir(parents=True)

        assert _portable_root((_PORTABLE,)) is None


class TestInstalledDevices:
    def test_reads_the_firmware_codes_and_platforms(self) -> None:
        _write(_PORTABLE / 'data' / 'devices.yml', _DEVICES_YML)

        assert _installed_devices(_PORTABLE / 'data') == [_NGAGE, _S60V3]

    def test_no_devices_file(self) -> None:
        assert _installed_devices(_PORTABLE / 'data') == []


class TestLaunchInfo:
    def test_android_shortcut_with_a_number(self) -> None:
        rom = _write(
            Path('/userdata/roms/ngage/Ashen - 6R21.json'),
            json.dumps({'AppUid': 270521321, 'AppName': 'Ashen', 'DeviceCode': 'NEM-4'}),
        )

        assert _read_launch_info(rom) == (0x101FD3E9, 'NEM-4')

    @pytest.mark.parametrize('uid', ['536902457', '0x20007B39'])
    def test_android_shortcut_with_a_string(self, uid: str) -> None:
        rom = _write(
            Path('/userdata/roms/ngage/launcher.json'),
            json.dumps({'AppUid': uid, 'AppName': 'NGAGE2 Launcher', 'DeviceCode': 'RM-409'}),
        )

        assert _read_launch_info(rom) == (0x20007B39, 'RM-409')

    @pytest.mark.parametrize('content', ['{"AppName": "x"}', '{"AppUid": "nope"}', '[]', 'not json'])
    def test_invalid(self, content: str) -> None:
        rom = _write(Path('/userdata/roms/ngage/bad.json'), content)

        with pytest.raises(BatoceraException):
            _read_launch_info(rom)


class TestSisInfo:
    def test_sisx(self) -> None:
        rom = _write(Path('/userdata/roms/symbian/game.sisx'), _uids(0x10201A7A, 0, 0x2000AFB9) + b'rest')

        assert _read_sis_info(rom) == SisInfo(0x2000AFB9, is_sisx=True)

    def test_old_sis(self) -> None:
        rom = _write(Path('/userdata/roms/symbian/game.sis'), _uids(0x101F4C3E, 0x1000006D, 0x10000419) + b'rest')

        assert _read_sis_info(rom) == SisInfo(0x101F4C3E, is_sisx=False)

    @pytest.mark.parametrize('content', [b'', b'short', _uids(1, 2, 3)])
    def test_not_a_sis(self, content: bytes) -> None:
        rom = _write(Path('/userdata/roms/symbian/game.sis'), content)

        with pytest.raises(BatoceraException):
            _read_sis_info(rom)


class TestGameCardUids:
    def test_reads_every_application_without_extracting(self) -> None:
        rom = Path('/userdata/roms/ngage/Ashen.zip')
        rom.parent.mkdir(parents=True)
        with zipfile.ZipFile(rom, 'w') as card:
            card.writestr('Ashen/System/Apps/6R21/6R21.aif', _uids(0x10000037, 0x0, 0x101FD3E9) + b'aif')
            card.writestr('Ashen/System/Apps/6R21/6R21.app', b'code')
            card.writestr('Ashen/System/Apps/6R21_1/6R21_1.AIF', _uids(0x10000037, 0x0, 0x101FD3EA))
            card.writestr('Ashen/System/Apps/6R21/readme.aif.txt', b'')

        assert _game_card_uids(rom) == [0x101FD3E9, 0x101FD3EA]

    def test_not_a_zip(self) -> None:
        assert _game_card_uids(_write(Path('/userdata/roms/ngage/bad.zip'), b'nope')) == []


class TestDevices:
    @pytest.mark.parametrize(
        ('devices', 'wanted', 'expected'),
        [
            ([_NGAGE, Device('RH-29', 'epoc6')], 'auto', 'RH-29'),
            ([_NGAGE, Device('RH-29', 'epoc6')], 'NEM-4', 'NEM-4'),
            ([_S60V3, _NGAGE], 'auto', 'NEM-4'),
        ],
    )
    def test_ngage(self, devices: list[Device], wanted: str, expected: str) -> None:
        assert _pick_ngage_device(devices, wanted).firmware_code == expected

    @pytest.mark.parametrize('wanted', ['auto', 'RH-29'])
    def test_ngage_missing(self, wanted: str) -> None:
        with pytest.raises(BatoceraException):
            _pick_ngage_device([_S60V3], wanted)

    def test_sis_by_kernel(self) -> None:
        assert _pick_sis_device([_NGAGE, _S60V3], SisInfo(1, is_sisx=True)) == _S60V3
        assert _pick_sis_device([_S60V3, _NGAGE], SisInfo(1, is_sisx=False)) == _NGAGE

    def test_sis_missing(self) -> None:
        with pytest.raises(BatoceraException):
            _pick_sis_device([_NGAGE], SisInfo(1, is_sisx=True))


class TestPackageInstalled:
    @pytest.mark.parametrize('drives', ['drives', 'drives/rm-409'])
    def test_registered(self, drives: str) -> None:
        storage = _PORTABLE / 'data'
        (storage / drives / 'c' / 'sys' / 'install' / 'sisregistry' / '2000afb9').mkdir(parents=True)

        assert _is_package_installed(storage, _S60V3, 0x2000AFB9)
        assert not _is_package_installed(storage, _S60V3, 0x2000AFBA)


class TestConfig:
    def test_keeps_the_other_settings(self) -> None:
        _write(_HOME / 'config.yml', 'cpu: dynarmic\ndata-storage: data\ninternet-bluetooth-friends:\n  []')

        _update_config(_PORTABLE / 'data', None, rtos_level='low', language=2)

        content = (_HOME / 'config.yml').read_text()
        assert 'cpu: dynarmic' in content
        assert f'data-storage: {_PORTABLE / "data"}' in content
        assert 'rtos-level: low' in content
        assert 'language: 2' in content
        assert 'stop-warn-touchscreen-disabled: true' in content

    def test_black_background_keeps_the_window_state(self) -> None:
        geometry = r'lastWindowGeometry=@ByteArray(\x1\xd9\xd0\xcb\0\x3\0\0)'
        _write(_HOME / 'EKA2L1.conf', f'[General]\nactiveUILanguage=C\n{geometry}\n')

        _update_config(_PORTABLE / 'data', None)

        assert (_HOME / 'EKA2L1.conf').read_text() == (
            '[General]\n'
            'activeUILanguage=C\n'
            f'{geometry}\n'
            r'backgroundDisplayColor=@Variant(\0\0\0\x43\x1\xff\xff\0\0\0\0\0\0\0\0)'
            '\n\n'
        )

    def test_links_the_portable_compat(self) -> None:
        _write(_PORTABLE / 'compat' / '101FD3E9.yml', 'fps: 30\n')
        _write(_HOME / 'compat' / '101FD3DE.yml', 'fps: 60\n')

        _update_config(_PORTABLE / 'data', _PORTABLE)

        assert (_HOME / 'compat').readlink() == _PORTABLE / 'compat'
        assert (_HOME / 'compat' / '101FD3E9.yml').read_text() == 'fps: 30\n'
        assert (_HOME / 'compat.batocera-backup' / '101FD3DE.yml').is_file()

    def test_relinks_once(self) -> None:
        (_PORTABLE / 'compat').mkdir(parents=True)
        _link_compat(_HOME, _PORTABLE / 'compat')
        _link_compat(_HOME, _PORTABLE / 'compat')

        assert (_HOME / 'compat').readlink() == _PORTABLE / 'compat'


class TestFps:
    def test_updates_the_game_settings(self) -> None:
        compat = _HOME / 'compat'
        _write(compat / '101FD3E9.yml', 'screen-upscale-method: 1\nfps: 60\ntime-delay: 0\n')

        _set_app_fps(compat, [0x101FD3E9, 0x101FD3EA], 30)

        assert (compat / '101FD3E9.yml').read_text() == 'screen-upscale-method: 1\nfps: 30\ntime-delay: 0\n'
        assert (compat / '101FD3EA.yml').read_text() == 'fps: 30\n'
