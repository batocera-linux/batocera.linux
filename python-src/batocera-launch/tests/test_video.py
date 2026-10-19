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

from batocera_launch.devices.video import parse_wayland_outputs

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
