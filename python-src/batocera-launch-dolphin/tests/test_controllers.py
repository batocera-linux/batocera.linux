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

from typing import TYPE_CHECKING

from batocera_launch_dolphin import controllers

from batocera_launch.devices.controller import Controller

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture

_NAME = 'DualSense Wireless Controller'


def _controller(index: int, /) -> Controller:
    return Controller(
        name=_NAME,
        type='joystick',
        guid='050000004c050000e60c000000810000',
        player_number=index + 1,
        index=index,
        real_name=_NAME,
        device_path=f'/dev/input/event{index}',
        button_count=13,
        hat_count=1,
        axis_count=6,
        inputs_={},
    )


def _profile(tmp_path: Path, filename: str, index: int, /) -> None:
    profiles = tmp_path / 'Profiles' / 'Wiimote'
    profiles.mkdir(parents=True, exist_ok=True)
    (profiles / filename).write_text(
        '[Profile]\n'
        f'Device = evdev/{index}/{_NAME}\n'
        'Buttons/A = `Button S`\n'
        f'IMUAccelerometer/Up = `evdev/{index}/{_NAME} Motion Sensors:Accel Y+`\n'
        f'Shake/X = `evdev/{index}/{_NAME}:Button E`\n'
        f'Profile = {filename}\n'
    )


def _sections(mocker: MockerFixture, tmp_path: Path, /) -> dict[str, list[str]]:
    mocker.patch.object(controllers, 'DOLPHIN_CONFIG', tmp_path)
    emulator = mocker.Mock(system='wii')
    emulator.config.get_bool.return_value = True

    controllers.generate_controller_config_any(
        emulator, [_controller(0), _controller(1)], {}, 'WiimoteNew.ini', 'Wiimote', {}, {}, None, {'Source': '1'}
    )

    sections: dict[str, list[str]] = {}
    current: list[str] = []
    for line in (tmp_path / 'WiimoteNew.ini').read_text(encoding='utf_8_sig').splitlines():
        if line.startswith('['):
            current = sections.setdefault(line, [])
        else:
            current.append(line)
    return sections


def test_each_pad_gets_its_own_profile(mocker: MockerFixture, tmp_path: Path) -> None:
    _profile(tmp_path, 'a.ini', 1)
    _profile(tmp_path, 'b.ini', 0)

    sections = _sections(mocker, tmp_path)

    assert 'Profile = b.ini' in sections['[Wiimote1]']
    assert f'IMUAccelerometer/Up = `evdev/0/{_NAME} Motion Sensors:Accel Y+`' in sections['[Wiimote1]']
    assert 'Profile = a.ini' in sections['[Wiimote2]']
    assert f'IMUAccelerometer/Up = `evdev/1/{_NAME} Motion Sensors:Accel Y+`' in sections['[Wiimote2]']


def test_shared_profile_follows_the_pad(mocker: MockerFixture, tmp_path: Path) -> None:
    _profile(tmp_path, 'a.ini', 0)

    sections = _sections(mocker, tmp_path)

    assert sections['[Wiimote1]'] == [
        f'Device = evdev/0/{_NAME}',
        'Source = 1',
        'Buttons/A = `Button S`',
        f'IMUAccelerometer/Up = `evdev/0/{_NAME} Motion Sensors:Accel Y+`',
        f'Shake/X = `evdev/0/{_NAME}:Button E`',
        'Profile = a.ini',
    ]
    assert sections['[Wiimote2]'] == [
        f'Device = evdev/1/{_NAME}',
        'Source = 1',
        'Buttons/A = `Button S`',
        f'IMUAccelerometer/Up = `evdev/1/{_NAME} Motion Sensors:Accel Y+`',
        f'Shake/X = `evdev/1/{_NAME}:Button E`',
        'Profile = a.ini',
    ]
