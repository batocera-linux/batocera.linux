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

from batocera_launch.config.config import Config
from batocera_launch.config.libretro import LibretroConfig
from batocera_launch_libretro import Libretro
from batocera_launch_libretro.cores.anybor import AnyBOR

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


@pytest.mark.parametrize(
    ('switchres', 'rotation', 'crt', 'orientation'),
    [
        ('1', '1', 'On', 'Vertical'),
        ('1', '3', 'On', 'Vertical'),
        ('1', '0', 'On', 'Horizontal'),
        ('1', '2', 'On', 'Horizontal'),
        ('1', 'auto', 'On', 'Horizontal'),
        ('1', None, 'On', 'Horizontal'),
        ('0', '1', 'Off', 'Horizontal'),
        (None, '3', 'Off', 'Horizontal'),
    ],
)
def test_anybor_crt_orientation(
    tmp_path: Path, mocker: MockerFixture, switchres: str | None, rotation: str | None, crt: str, orientation: str
) -> None:
    config = Config({'retroarch.crt_switch_resolution': switchres, 'display.rotate': rotation})
    core = AnyBOR(mocker.Mock(spec=Libretro, config=config))
    options = LibretroConfig(tmp_path / 'retroarch-core-options.cfg', config)
    options.set('anybor_os_screen_orientation', 'Vertical' if orientation == 'Horizontal' else 'Horizontal')

    core.set_core_options(options)

    assert options.key_value_config['anybor_crt_tv'] == f'"{crt}"'
    assert options.key_value_config['anybor_os_screen_orientation'] == f'"{orientation}"'
