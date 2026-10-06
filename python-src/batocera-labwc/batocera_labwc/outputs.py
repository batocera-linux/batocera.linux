from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING, NotRequired, TypedDict

if TYPE_CHECKING:
    from collections.abc import Iterable

_logger = logging.getLogger(__name__)


class _Position(TypedDict):
    x: int
    y: int


class _Mode(TypedDict):
    width: int
    height: int
    current: NotRequired[bool]


class _Output(TypedDict):
    name: str
    enabled: bool
    modes: list[_Mode]
    position: NotRequired[_Position]
    transform: NotRequired[str]
    scale: NotRequired[float]


@dataclass(slots=True, frozen=True)
class Box:
    x: int
    y: int
    width: int
    height: int


def _output_box(output: _Output, /) -> Box | None:
    mode = next((mode for mode in output['modes'] if mode.get('current')), None)
    if mode is None:
        return None

    width, height = mode['width'], mode['height']
    if output.get('transform', 'normal').endswith(('90', '270')):
        width, height = height, width

    scale = output.get('scale', 1.0) or 1.0
    position = output.get('position', {'x': 0, 'y': 0})

    return Box(position['x'], position['y'], round(width / scale), round(height / scale))


def layout_box(names: Iterable[str], /) -> Box | None:
    """Bounding box in layout coordinates of the named, enabled outputs."""
    try:
        proc = subprocess.run(['wlr-randr', '--json'], capture_output=True, check=True, text=True)
        outputs: list[_Output] = json.loads(proc.stdout)
    except OSError, subprocess.CalledProcessError, ValueError:
        _logger.exception('failed to read the output layout.')
        return None

    wanted = set(names)
    boxes = [
        box
        for output in outputs
        if output['name'] in wanted and output['enabled'] and (box := _output_box(output)) is not None
    ]

    if not boxes:
        return None

    left = min(box.x for box in boxes)
    top = min(box.y for box in boxes)
    right = max(box.x + box.width for box in boxes)
    bottom = max(box.y + box.height for box in boxes)

    return Box(left, top, right - left, bottom - top)
