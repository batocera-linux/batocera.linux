from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

from batocera_labwc.outputs import Box, layout_box

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

_OUTPUTS = [
    {
        'name': 'DP-1',
        'enabled': True,
        'position': {'x': 0, 'y': 0},
        'transform': '90',
        'scale': 1.0,
        'modes': [{'width': 1080, 'height': 1920, 'current': True}],
    },
    {
        'name': 'DSI-1',
        'enabled': True,
        'position': {'x': 320, 'y': 1080},
        'transform': 'normal',
        'scale': 1.0,
        'modes': [{'width': 1280, 'height': 960}, {'width': 1280, 'height': 960, 'current': True}],
    },
    {
        'name': 'HDMI-A-1',
        'enabled': False,
        'position': {'x': 5000, 'y': 5000},
        'modes': [{'width': 1920, 'height': 1080, 'current': True}],
    },
]


def _mock_wlr_randr(mocker: MockerFixture, outputs: object, /) -> None:
    mocker.patch(
        'batocera_labwc.outputs.subprocess.run',
        return_value=subprocess.CompletedProcess([], 0, stdout=json.dumps(outputs)),
    )


def test_layout_box_spans_rotated_and_offset_outputs(mocker: MockerFixture) -> None:
    _mock_wlr_randr(mocker, _OUTPUTS)

    assert layout_box(('DP-1', 'DSI-1')) == Box(0, 0, 1920, 2040)


def test_layout_box_ignores_disabled_and_unnamed_outputs(mocker: MockerFixture) -> None:
    _mock_wlr_randr(mocker, _OUTPUTS)

    assert layout_box(('DSI-1', 'HDMI-A-1')) == Box(320, 1080, 1280, 960)


def test_layout_box_applies_scale(mocker: MockerFixture) -> None:
    _mock_wlr_randr(
        mocker,
        [{'name': 'eDP-1', 'enabled': True, 'scale': 2.0, 'modes': [{'width': 2560, 'height': 1600, 'current': True}]}],
    )

    assert layout_box(('eDP-1',)) == Box(0, 0, 1280, 800)


def test_layout_box_without_matching_outputs(mocker: MockerFixture) -> None:
    _mock_wlr_randr(mocker, [{'name': 'DSI-1', 'enabled': True, 'modes': [{'width': 1280, 'height': 960}]}])

    assert layout_box(('DSI-1', 'DP-1')) is None


def test_layout_box_when_wlr_randr_fails(mocker: MockerFixture) -> None:
    mocker.patch('batocera_labwc.outputs.subprocess.run', side_effect=subprocess.CalledProcessError(1, 'wlr-randr'))

    assert layout_box(('DSI-1',)) is None
