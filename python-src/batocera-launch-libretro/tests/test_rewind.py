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

from batocera_launch.config.config import Config, SystemConfig
from batocera_launch.config.libretro import LibretroConfig
from batocera_launch.types import Resolution
from batocera_launch_libretro import Libretro, RACore
from batocera_launch_libretro.core import Core
from batocera_launch_libretro.cores.anybor import AnyBOR
from batocera_launch_libretro.libretro_info import LibretroInfo

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


async def test_rewind_defaults_are_written_for_each_core(tmp_path: Path, mocker: MockerFixture) -> None:
    custom_path = tmp_path / 'retroarchcustom.cfg'
    info = mocker.Mock(spec=LibretroInfo)
    info.get_bool.return_value = True
    info.get.return_value = 'deterministic'
    mocker.patch.object(Core, 'info', mocker.PropertyMock(return_value=info))
    config = Config({'rewind': True})
    emulator = mocker.Mock(
        spec=Libretro,
        config=mocker.Mock(spec=SystemConfig, wraps=config, show_fps=False),
        controllers=[],
        es_settings=Config({}),
        resolution=Resolution(640, 480),
        render_config=Config({}),
        config_dir=tmp_path,
        saves_dir=tmp_path,
    )

    for core, granularity, buffer_size, enabled in (
        (AnyBOR, 10, 256, True),
        (RACore, 1, 20, True),
        (AnyBOR, 10, 256, True),
        (Core, 1, 20, False),
    ):
        config['rewind'] = enabled
        emulator.lr_core = core(emulator)
        custom_config = LibretroConfig(custom_path, config)
        await Libretro.set_config(emulator, custom_config, 'gl', False)
        custom_config.write()

        settings = LibretroConfig(custom_path, config).key_value_config
        assert settings['rewind_enable'] == ('"true"' if enabled else '"false"')
        assert settings['rewind_granularity'] == f'"{granularity}"'
        assert settings['rewind_buffer_size'] == f'"{buffer_size}"'
