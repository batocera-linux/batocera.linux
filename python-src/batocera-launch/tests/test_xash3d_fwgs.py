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
    from pyfakefs.fake_filesystem import FakeFilesystem
    from pytest_mock import MockerFixture

    from batocera_launch import SystemConfig
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


@pytest.mark.launch_config_emulator('xash3d_fwgs')
@pytest.mark.launch_config_system('halflife')
@pytest.mark.launch_rom_source('/userdata/roms/halflife/cstrike.game')
async def test_game_dir_libs_are_used_when_shipped(
    fake_fs: FakeFilesystem, mocker: MockerFixture, launch_config: SystemConfig, launch_rom: Rom
) -> None:
    mocker.patch('batocera_launch.emulators.xash3d_fwgs.emulator._get_arch_suffix', return_value='_amd64')
    mocker.patch.object(Xash3dFwgs, '_maybe_init_config')
    mocker.patch.object(Xash3dFwgs, '_maybe_init_save_dir')
    game_dir = Path('/userdata/roms/halflife/cstrike')
    fake_fs.create_file(game_dir / 'liblist.gam', contents='gamedll "dlls\\mp.dll"\ngamedll_linux "dlls/cs.so"\n')
    fake_fs.create_file(game_dir / 'cl_dlls' / 'client_amd64.so')
    fake_fs.create_file(game_dir / 'dlls' / 'cs_amd64.so')

    xash3d = Xash3dFwgs(config=launch_config, profiler=mocker.Mock())
    xash3d.rom = launch_rom
    command = await xash3d.configure()

    assert str(command.args[command.args.index('-clientlib') + 1]) == f'{game_dir}/cl_dlls/client_amd64.so'
    assert str(command.args[command.args.index('-dll') + 1]) == f'{game_dir}/dlls/cs_amd64.so'


@pytest.mark.launch_config_emulator('xash3d_fwgs')
@pytest.mark.launch_config_system('halflife')
@pytest.mark.launch_rom_source('/userdata/roms/halflife/cstrike.game')
async def test_hlsdk_libs_are_used_when_game_dir_ships_only_one(
    fake_fs: FakeFilesystem, mocker: MockerFixture, launch_config: SystemConfig, launch_rom: Rom
) -> None:
    mocker.patch('batocera_launch.emulators.xash3d_fwgs.emulator._get_arch_suffix', return_value='_amd64')
    mocker.patch.object(Xash3dFwgs, '_maybe_init_config')
    mocker.patch.object(Xash3dFwgs, '_maybe_init_save_dir')
    game_dir = Path('/userdata/roms/halflife/cstrike')
    fake_fs.create_file(game_dir / 'liblist.gam', contents='gamedll_linux "dlls/cs.so"\n')
    fake_fs.create_file(game_dir / 'dlls' / 'cs_amd64.so')

    xash3d = Xash3dFwgs(config=launch_config, profiler=mocker.Mock())
    xash3d.rom = launch_rom
    command = await xash3d.configure()

    assert str(command.args[command.args.index('-clientlib') + 1]) == '/usr/lib/xash3d/hlsdk/hl/cl_dlls/client_amd64.so'
    assert str(command.args[command.args.index('-dll') + 1]) == '/usr/lib/xash3d/hlsdk/hl/dlls/hl_amd64.so'
