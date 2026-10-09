from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest

from batocera_common.paths import BATOCERA_CONF, SYSCONFIG
from batocera_labwc.touch import (
    BATOCERA_RESOLUTION,
    BATOCERA_SETTINGS_SET,
    LIBINPUT,
    TouchMapping,
    resolve_touchscreens,
    touchscreens,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.usefixtures('fs')

_LIBINPUT_LIST = """\
Device:           gpio-keys
Kernel:           /dev/input/event0
Capabilities:     keyboard

Device:           Synaptics SM42TM
Kernel:           /dev/input/event5
Capabilities:     touch

Device:           Odin2 Gamepad
Kernel:           /dev/input/event6
Capabilities:     keyboard pointer

Device:           RetroidPocket RDS Touchscreen
Kernel:           /dev/input/event7
Capabilities:     touch
"""


def _conf(user: str = '', system: str = '') -> None:
    BATOCERA_CONF.parent.mkdir(parents=True, exist_ok=True)
    BATOCERA_CONF.write_text(user)
    SYSCONFIG.parent.mkdir(parents=True, exist_ok=True)
    SYSCONFIG.write_text(system)


def _mock_commands(mocker: MockerFixture, models: dict[str, str] | None = None) -> list[tuple[str, ...]]:
    calls: list[tuple[str, ...]] = []

    def run(command: tuple[str, ...], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        if command == (LIBINPUT, 'list-devices'):
            return subprocess.CompletedProcess(command, 0, _LIBINPUT_LIST, '')
        if command[0] == BATOCERA_RESOLUTION and command[3] == 'outputModel':
            return subprocess.CompletedProcess(command, 0, f'{(models or {}).get(command[2], "")}\n', '')
        if command[0] == BATOCERA_SETTINGS_SET:
            return subprocess.CompletedProcess(command, 0, '', '')
        raise AssertionError(command)  # pragma: no cover

    mocker.patch('batocera_labwc.touch.subprocess.run', side_effect=run)
    return calls


def _learnt(calls: list[tuple[str, ...]]) -> list[tuple[str, str]]:
    return [(call[1], call[2]) for call in calls if call[0] == BATOCERA_SETTINGS_SET]


def test_touchscreens(mocker: MockerFixture) -> None:
    _mock_commands(mocker)

    assert touchscreens() == ['Synaptics SM42TM', 'RetroidPocket RDS Touchscreen']


def test_touchscreens_without_libinput(mocker: MockerFixture) -> None:
    mocker.patch('batocera_labwc.touch.subprocess.run', side_effect=FileNotFoundError)

    assert touchscreens() == []


def test_lone_touchscreen_is_learnt_for_the_only_output(
    mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    _conf()
    calls = _mock_commands(mocker)

    assert resolve_touchscreens(['DSI-1'], ['Synaptics SM42TM']) == [TouchMapping('Synaptics SM42TM', 'DSI-1', None)]
    assert _learnt(calls) == [('display.touchscreen.DSI-1', 'Synaptics SM42TM')]
    assert 'learnt for output DSI-1' in capsys.readouterr().out


def test_learnt_setting_keeps_touch_on_its_output_when_docked(mocker: MockerFixture) -> None:
    _conf(user='display.touchscreen.DSI-1=Synaptics SM42TM\n')
    calls = _mock_commands(mocker, {'DP-1': 'Dell_U2720Q'})

    assert resolve_touchscreens(['DP-1', 'DSI-1'], ['Synaptics SM42TM']) == [
        TouchMapping('Synaptics SM42TM', 'DSI-1', None)
    ]
    assert _learnt(calls) == []


def test_lone_touchscreen_with_several_outputs_falls_back_to_primary(
    mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    _conf()
    calls = _mock_commands(mocker)

    assert resolve_touchscreens(['DP-1', 'DSI-1'], ['Synaptics SM42TM']) == [
        TouchMapping('Synaptics SM42TM', 'DP-1', None)
    ]
    assert _learnt(calls) == []
    assert 'cannot be told apart between DP-1, DSI-1; using DP-1' in capsys.readouterr().out


def test_external_touchscreen_is_learnt_by_model(mocker: MockerFixture) -> None:
    _conf(system='display.touchscreen.DSI-1=Synaptics SM42TM\ndisplay.touchrotate.Lontium=1\n')
    calls = _mock_commands(mocker, {'DP-1': 'Lontium'})

    assert resolve_touchscreens(['DP-1', 'DSI-1'], ['Synaptics SM42TM', 'RetroidPocket RDS Touchscreen']) == [
        TouchMapping('Synaptics SM42TM', 'DSI-1', None),
        TouchMapping('RetroidPocket RDS Touchscreen', 'DP-1', 1),
    ]
    assert _learnt(calls) == [('display.touchscreen.Lontium', 'RetroidPocket RDS Touchscreen')]


def test_settings_are_matched_by_model_then_connector(mocker: MockerFixture) -> None:
    _conf(
        user='display.touchscreen.Lontium=RetroidPocket RDS Touchscreen\ndisplay.touchrotate.DP-1=3\n',
        system='display.touchrotate.Lontium=1\n',
    )
    _mock_commands(mocker, {'DP-1': 'Lontium'})

    assert resolve_touchscreens(['DP-1'], ['RetroidPocket RDS Touchscreen']) == [
        TouchMapping('RetroidPocket RDS Touchscreen', 'DP-1', 3)
    ]


def test_two_touchscreens_sharing_outputs_stay_unmapped(
    mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    _conf()
    calls = _mock_commands(mocker)

    assert resolve_touchscreens(['DSI-1', 'DSI-2'], ['top', 'bottom']) == []
    assert _learnt(calls) == []
    assert 'Touchscreens top, bottom left unmapped' in capsys.readouterr().out


def test_configured_touchscreen_claims_its_output_while_absent(
    mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    _conf(system='display.touchscreen.DSI-1=Synaptics SM42TM\n')
    calls = _mock_commands(mocker)

    assert resolve_touchscreens(['DSI-1'], ['Other']) == [TouchMapping('Synaptics SM42TM', 'DSI-1', None)]
    assert _learnt(calls) == []
    assert "'Synaptics SM42TM' mapped to output DSI-1 (not connected)" in capsys.readouterr().out


def test_lone_touchscreen_on_the_claimed_primary_is_left_alone(mocker: MockerFixture) -> None:
    _conf(system='display.touchscreen.DP-1=Other\n')
    _mock_commands(mocker)

    assert resolve_touchscreens(['DP-1', 'DSI-1', 'HDMI-A-1'], ['Synaptics SM42TM']) == [
        TouchMapping('Other', 'DP-1', None)
    ]


def test_invalid_rotation_is_ignored(mocker: MockerFixture) -> None:
    _conf(system='display.touchscreen.DSI-1=Synaptics SM42TM\ndisplay.touchrotate.DSI-1=left\n')
    _mock_commands(mocker)

    assert resolve_touchscreens(['DSI-1'], ['Synaptics SM42TM']) == [TouchMapping('Synaptics SM42TM', 'DSI-1', None)]


def test_configured_touchscreen_is_not_learnt_again_when_its_output_is_off(
    mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    _conf(user='display.touchscreen.DSI-1=Synaptics SM42TM\n')
    calls = _mock_commands(mocker, {'DP-1': 'SONY_TV___00'})

    assert resolve_touchscreens(['DP-1'], ['Synaptics SM42TM']) == []
    assert _learnt(calls) == []
    assert "'Synaptics SM42TM' is configured for an output that is not active" in capsys.readouterr().out


def test_no_touchscreen(mocker: MockerFixture, capsys: pytest.CaptureFixture[str]) -> None:
    _conf()
    _mock_commands(mocker)

    assert resolve_touchscreens(['DP-1', 'HDMI-A-1'], []) == []
    assert 'No touchscreen found.' in capsys.readouterr().out
