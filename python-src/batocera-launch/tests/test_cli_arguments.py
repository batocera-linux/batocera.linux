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
from __future__ import annotations

from pathlib import Path

from batocera_launch.cli.arguments import Arguments


def _arguments(netplaypass: str | None) -> Arguments:
    return Arguments(
        system='snes',
        rom=Path('/userdata/roms/snes/game.sfc'),
        emulator=None,
        core=None,
        players=(),
        netplaymode=None,
        netplaypass=netplaypass,
        netplayip=None,
        netplayport=None,
        netplaysession=None,
        state_slot=None,
        state_filename=None,
        autosave=None,
        systemname=None,
        gameinfoxml=Path('gameinfo.xml'),
        lightgun=False,
        wheel=False,
        trackball=False,
        spinner=False,
    )


def test_arguments_repr_does_not_leak_netplay_password() -> None:
    sentinel = 'NETPLAY_PASSWORD_SENTINEL'

    assert sentinel not in repr(_arguments(sentinel))


def test_arguments_keep_netplay_password_value() -> None:
    assert _arguments('pw').netplaypass == 'pw'
