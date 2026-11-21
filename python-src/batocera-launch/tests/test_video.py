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

from batocera_launch.devices.video import find_screen, parse_wayland_outputs
from batocera_launch.types import Resolution, ScreenInfo

# wayland-info -i wl_output on a dual panel device
_WAYLAND_INFO = """\
interface: 'wl_output',                                  version:  4, name: 58
\tname: DSI-1
\tdescription: (null) (null) (DSI-1)
\tx: 0, y: 0, scale: 1,
\tmodes:
\t\twidth: 1920, height: 1080, refresh: 60.000 Hz, flags: current preferred
interface: 'wl_output',                                  version:  4, name: 59
\tname: DSI-2
\tdescription: (null) (null) (DSI-2)
"""


def test_parse_wayland_outputs_keeps_registry_order() -> None:
    assert parse_wayland_outputs(_WAYLAND_INFO) == ['DSI-1', 'DSI-2']


def test_parse_wayland_outputs_empty() -> None:
    assert parse_wayland_outputs('') == []


def test_find_screen_tertiary() -> None:
    screens = [ScreenInfo(name, Resolution(1920, 1080), 1920 * i, 0) for i, name in enumerate(('DP-1', 'DP-3', 'DP-2'))]

    assert find_screen(screens, 'tertiary') == screens[2]
    assert find_screen(screens[:2], 'tertiary') is None
