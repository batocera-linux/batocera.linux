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

import sys
from typing import TYPE_CHECKING

from batocera_launch.cli.arguments import Arguments

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_repr_hides_netplay_password(mocker: MockerFixture) -> None:
    mocker.patch.object(
        sys,
        'argv',
        ['batocera-launch', '-system', 'snes', '-rom', '/userdata/roms/snes/game.sfc', '-netplaypass', 'hunter2'],
    )

    args = Arguments.parse(1)

    assert args.netplaypass == 'hunter2'
    assert 'hunter2' not in repr(args)
