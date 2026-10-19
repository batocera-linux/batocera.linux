from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from xml.etree import ElementTree as ET

import pytest
from batocera_launch_mame.emulator import MAME

import batocera_launch_mame_common
from batocera_launch.devices.controller import Controller
from batocera_launch.devices.input import Input

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from batocera_launch import SystemConfig
    from batocera_launch.rom import Rom

_RESOURCES = Path(batocera_launch_mame_common.__file__).parent.parent / 'resources'


def _controller(index: int, /, *, stick: bool = True) -> Controller:
    inputs = {
        'up': Input(name='up', type='hat', id='0', value='1'),
        'down': Input(name='down', type='hat', id='0', value='4'),
        'left': Input(name='left', type='hat', id='0', value='8'),
        'right': Input(name='right', type='hat', id='0', value='2'),
        'b': Input(name='b', type='button', id='0', value='1'),
    }
    if stick:
        inputs['joystick1left'] = Input(name='joystick1left', type='axis', id='0', value='-1')
        inputs['joystick1up'] = Input(name='joystick1up', type='axis', id='1', value='-1')

    return Controller(
        name='Test Pad',
        type='joystick',
        guid='050000005e0400008e02000030110000',
        player_number=index + 1,
        index=index,
        real_name='Test Pad',
        device_path=f'/dev/input/event{index}',
        button_count=11,
        hat_count=1,
        axis_count=4 if stick else 0,
        inputs_=inputs,
    )


def _adstick_ports(
    mocker: MockerFixture,
    tmp_path: Path,
    config: SystemConfig,
    rom: Rom,
    controllers: list[Controller],
    gun_count: int,
    /,
) -> dict[str, str]:
    for module in ('mame_controls', 'mess_system_info'):
        mocker.patch(f'batocera_launch_mame_common.{module}.MAME_DATA_DIR', _RESOURCES)

    mame = MAME(config=config, profiler=mocker.Mock())
    mame.rom = rom
    mame.controllers = controllers
    mame.guns = [mocker.Mock() for _ in range(gun_count)]
    mame.wheels = {}
    mame.write_control_config(tmp_path, 'mame', 'none', False)

    ports = ET.parse(tmp_path / 'default.cfg').getroot().iterfind('.//port')
    return {
        port.attrib['type']: ' '.join(newseq.text or '' for newseq in port.iterfind('newseq'))
        for port in ports
        if '_AD_STICK_' in port.attrib['type']
    }


@pytest.mark.launch_config_emulator('mame')
@pytest.mark.launch_config_user_settings({'altlayout': 'default'})
def test_pad_stick_without_guns(
    mocker: MockerFixture, tmp_path: Path, launch_config: SystemConfig, launch_rom: Rom
) -> None:
    assert _adstick_ports(mocker, tmp_path, launch_config, launch_rom, [_controller(0), _controller(1)], 0) == {
        'P1_AD_STICK_X': 'JOYCODE_1_XAXIS OR MOUSECODE_1_XAXIS',
        'P1_AD_STICK_Y': 'JOYCODE_1_YAXIS OR MOUSECODE_1_YAXIS',
        'P2_AD_STICK_X': 'JOYCODE_2_XAXIS OR MOUSECODE_2_XAXIS',
        'P2_AD_STICK_Y': 'JOYCODE_2_YAXIS OR MOUSECODE_2_YAXIS',
    }


@pytest.mark.launch_config_emulator('mame')
@pytest.mark.launch_config_user_settings({'altlayout': 'default', 'use_guns': '1'})
def test_pad_stick_when_no_gun_is_found(
    mocker: MockerFixture, tmp_path: Path, launch_config: SystemConfig, launch_rom: Rom
) -> None:
    assert _adstick_ports(mocker, tmp_path, launch_config, launch_rom, [_controller(0)], 0) == {
        'P1_AD_STICK_X': 'JOYCODE_1_XAXIS OR MOUSECODE_1_XAXIS',
        'P1_AD_STICK_Y': 'JOYCODE_1_YAXIS OR MOUSECODE_1_YAXIS',
    }


@pytest.mark.launch_config_emulator('mame')
@pytest.mark.launch_config_user_settings({'altlayout': 'default', 'use_guns': '1'})
def test_gun_only_for_players_with_a_gun(
    mocker: MockerFixture, tmp_path: Path, launch_config: SystemConfig, launch_rom: Rom
) -> None:
    assert _adstick_ports(mocker, tmp_path, launch_config, launch_rom, [_controller(0), _controller(1)], 1) == {
        'P1_AD_STICK_X': 'GUNCODE_1_XAXIS',
        'P1_AD_STICK_Y': 'GUNCODE_1_YAXIS',
        'P2_AD_STICK_X': 'JOYCODE_2_XAXIS OR MOUSECODE_2_XAXIS',
        'P2_AD_STICK_Y': 'JOYCODE_2_YAXIS OR MOUSECODE_2_YAXIS',
    }


@pytest.mark.launch_config_emulator('mame')
@pytest.mark.launch_config_user_settings({'altlayout': 'default', 'use_guns': '1'})
def test_guns_beyond_the_pads(
    mocker: MockerFixture, tmp_path: Path, launch_config: SystemConfig, launch_rom: Rom
) -> None:
    assert _adstick_ports(mocker, tmp_path, launch_config, launch_rom, [_controller(0)], 2) == {
        'P1_AD_STICK_X': 'GUNCODE_1_XAXIS',
        'P1_AD_STICK_Y': 'GUNCODE_1_YAXIS',
        'P2_AD_STICK_X': 'GUNCODE_2_XAXIS',
        'P2_AD_STICK_Y': 'GUNCODE_2_YAXIS',
    }


@pytest.mark.launch_config_emulator('mame')
@pytest.mark.launch_config_user_settings({'altlayout': 'default'})
def test_pad_without_stick_keeps_mame_defaults(
    mocker: MockerFixture, tmp_path: Path, launch_config: SystemConfig, launch_rom: Rom
) -> None:
    assert _adstick_ports(mocker, tmp_path, launch_config, launch_rom, [_controller(0, stick=False)], 0) == {}
