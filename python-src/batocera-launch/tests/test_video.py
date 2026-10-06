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
