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

from batocera_launch_libretro import Libretro
from batocera_launch_libretro.core import Core
from batocera_launch_libretro.libretro_info import LibretroInfo

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

STATE_KEYS = {'save_state', 'restore_state', 'previous_slot', 'next_slot'}


@pytest.mark.parametrize(
    ('savestate', 'registered'),
    [(False, False), (True, True), (None, True)],
)
def test_state_hotkeys_follow_the_cores_savestate_support(
    mocker: MockerFixture, savestate: bool | None, registered: bool
) -> None:
    info = mocker.Mock(spec=LibretroInfo)
    info.get_bool.return_value = savestate
    info.get.return_value = None
    mocker.patch.object(Core, 'info', mocker.PropertyMock(return_value=info))
    emulator = mocker.Mock(spec=Libretro)
    emulator.lr_core = Core(emulator)

    keys = Libretro.hotkeygen_context.func(emulator)['keys']

    assert (keys.keys() >= STATE_KEYS) is registered
    assert STATE_KEYS.isdisjoint(keys) is not registered
    assert 'exit' in keys
