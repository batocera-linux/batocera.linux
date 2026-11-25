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

import pytest
from batocera_launch_mame.emulator import MAME

from batocera_launch.savestates.manager import release_state_manager
from batocera_launch.savestates.spec import SaveStateSpec

if TYPE_CHECKING:
    from collections.abc import Iterator

    from pytest_mock import MockerFixture

    from batocera_launch import SystemConfig
    from batocera_launch.rom import Rom


@pytest.fixture(autouse=True)
def spec(mocker: MockerFixture, launch_config: SystemConfig) -> Iterator[None]:
    data = {
        'directory': 'mame/state/{{system}}',
        'file': '{{romfilename}}.{{slot0}}.sta',
        'boot': {'args': ['-state', '{file}']},
    }
    mocker.patch('batocera_launch.savestates.manager.load_spec', return_value=SaveStateSpec.from_dict(data))
    yield
    release_state_manager(launch_config)


def _mame(mocker: MockerFixture, config: SystemConfig, rom: Rom, /) -> MAME:
    mame = MAME(config=config, profiler=mocker.Mock())
    mame.rom = rom
    return mame


@pytest.mark.launch_config_emulator('mame')
@pytest.mark.launch_rom_source('/userdata/roms/nes/Super Mario Bros. (USA).zip')
@pytest.mark.launch_rom_prepared('/var/run/batocera-launch/rom/Super Mario Bros. (USA).nes')
@pytest.mark.launch_config_user_settings({'state_slot': '3'})
def test_statename_is_the_source_rom(mocker: MockerFixture, launch_config: SystemConfig, launch_rom: Rom) -> None:
    assert _mame(mocker, launch_config, launch_rom).state_args == ['-statename', 'Super Mario Bros. (USA).zip']


@pytest.mark.launch_config_emulator('mame')
@pytest.mark.launch_rom_source('/userdata/roms/mame/sf2.zip')
@pytest.mark.launch_config_user_settings(
    {'state_slot': '2', 'state_filename': '/userdata/saves/mame/state/mame/sf2.2.sta'}
)
def test_state_file_is_loaded_at_start(mocker: MockerFixture, launch_config: SystemConfig, launch_rom: Rom) -> None:
    assert _mame(mocker, launch_config, launch_rom).state_args == [
        '-statename',
        'sf2.zip',
        '-state',
        '/userdata/saves/mame/state/mame/sf2.2.sta',
    ]
