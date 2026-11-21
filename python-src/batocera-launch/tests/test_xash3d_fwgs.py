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

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from batocera_launch.emulators.xash3d_fwgs import Xash3dFwgs

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from batocera_launch import Command, SystemConfig
    from batocera_launch.rom import Rom


@pytest.mark.launch_config_emulator('xash3d_fwgs')
@pytest.mark.launch_config_system('halflife')
@pytest.mark.launch_rom_source('/userdata/roms/halflife/valve.game')
async def test_basedir_is_the_system_folder(
    mocker: MockerFixture, launch_config: SystemConfig, launch_rom: Rom
) -> None:
    mocker.patch('batocera_launch.emulators.xash3d_fwgs.emulator._get_arch_suffix', return_value='_amd64')
    mocker.patch.object(Xash3dFwgs, '_maybe_init_config')
    mocker.patch.object(Xash3dFwgs, '_maybe_init_save_dir')

    xash3d = Xash3dFwgs(config=launch_config, profiler=mocker.Mock())
    xash3d.rom = launch_rom
    command = await xash3d.configure()

    assert command.env['XASH3D_BASEDIR'] == Path('/userdata/roms/halflife')
    assert command.args[command.args.index('-game') + 1] == 'valve'


_LIBS = Path('/usr/lib/xash3d/hlsdk')


async def _configure(mocker: MockerFixture, launch_config: SystemConfig, launch_rom: Rom) -> Command:
    mocker.patch('batocera_launch.emulators.xash3d_fwgs.emulator._get_arch_suffix', return_value='_amd64')
    mocker.patch.object(Xash3dFwgs, '_maybe_init_config')
    mocker.patch.object(Xash3dFwgs, '_maybe_init_save_dir')

    xash3d = Xash3dFwgs(config=launch_config, profiler=mocker.Mock())
    xash3d.rom = launch_rom
    return await xash3d.configure()


def _create_file(path: Path | str, contents: str = '') -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents)


def _create_libs(name: str, server: str) -> None:
    _create_file(_LIBS / name / 'cl_dlls' / 'client_amd64.so')
    _create_file(_LIBS / name / 'dlls' / f'{server}_amd64.so')


@pytest.mark.launch_config_emulator('xash3d_fwgs')
@pytest.mark.launch_config_system('halflife')
@pytest.mark.launch_rom_source('/userdata/roms/halflife/bshift.game')
@pytest.mark.usefixtures('fake_fs')
async def test_libs_are_picked_by_game_dir_before_gamedll(
    mocker: MockerFixture, launch_config: SystemConfig, launch_rom: Rom
) -> None:
    _create_libs('hl', 'hl')
    _create_libs('bshift', 'bshift')
    _create_file('/userdata/roms/halflife/bshift/liblist.gam', contents='gamedll "dlls\\hl.dll"\n')

    command = await _configure(mocker, launch_config, launch_rom)

    assert command.args[command.args.index('-clientlib') + 1] == _LIBS / 'bshift' / 'cl_dlls' / 'client_amd64.so'
    assert command.args[command.args.index('-dll') + 1] == _LIBS / 'bshift' / 'dlls' / 'bshift_amd64.so'
    assert '-menulib' not in command.args
    assert 'XASH3D_EXTRAS_PAK2' not in command.env


@pytest.mark.launch_config_emulator('xash3d_fwgs')
@pytest.mark.launch_config_system('halflife')
@pytest.mark.launch_rom_source('/userdata/roms/halflife/gearbox.game')
@pytest.mark.usefixtures('fake_fs')
async def test_libs_fall_back_to_gamedll(mocker: MockerFixture, launch_config: SystemConfig, launch_rom: Rom) -> None:
    _create_libs('hl', 'hl')
    _create_libs('opfor', 'opfor')
    _create_file('/userdata/roms/halflife/gearbox/liblist.gam', contents='gamedll "dlls\\opfor.dll"\n')

    command = await _configure(mocker, launch_config, launch_rom)

    assert command.args[command.args.index('-clientlib') + 1] == _LIBS / 'opfor' / 'cl_dlls' / 'client_amd64.so'
    assert command.args[command.args.index('-dll') + 1] == _LIBS / 'opfor' / 'dlls' / 'opfor_amd64.so'


@pytest.mark.launch_config_emulator('xash3d_fwgs')
@pytest.mark.launch_config_system('halflife')
@pytest.mark.launch_rom_source('/userdata/roms/halflife/cstrike.game')
@pytest.mark.usefixtures('fake_fs')
async def test_cstrike_uses_its_menu_and_extras(
    mocker: MockerFixture, launch_config: SystemConfig, launch_rom: Rom
) -> None:
    _create_libs('hl', 'hl')
    _create_libs('cstrike', 'cs')
    _create_file(_LIBS / 'cstrike' / 'cl_dlls' / 'menu_amd64.so')
    _create_file('/usr/share/xash3d/cstrike/extras.pk3')
    _create_file(
        '/userdata/roms/halflife/cstrike/liblist.gam', contents='gamedll "dlls\\mp.dll"\ngamedll_linux "dlls/cs.so"\n'
    )

    command = await _configure(mocker, launch_config, launch_rom)

    assert command.args[command.args.index('-dll') + 1] == _LIBS / 'cstrike' / 'dlls' / 'cs_amd64.so'
    assert command.args[command.args.index('-menulib') + 1] == _LIBS / 'cstrike' / 'cl_dlls' / 'menu_amd64.so'
    assert str(command.env['XASH3D_EXTRAS_PAK2']) == '/usr/share/xash3d/cstrike/extras.pk3'
