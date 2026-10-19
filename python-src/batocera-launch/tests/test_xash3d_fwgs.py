from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from batocera_launch.emulators.xash3d_fwgs import Xash3dFwgs

if TYPE_CHECKING:
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
