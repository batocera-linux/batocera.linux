from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self, TypedDict, cast

_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path


@dataclass(slots=True, frozen=True)
class Resolution:
    width: int
    height: int


class HotkeysContext(TypedDict):
    name: str
    keys: dict[str, Sequence[str]]  # Sequence[str] covers both str and list[str]


@dataclass(slots=True, frozen=True)
class BezelFiles:
    png: Path
    info: Path
    layout: Path
    mame_zip: Path
    specific_to_game: bool


@dataclass(slots=True, frozen=True)
class BezelInfo:
    width: int | None
    height: int | None
    top: int | None
    bottom: int | None
    left: int | None
    right: int | None
    opacity: float | None
    message_x: float | None
    message_y: float | None

    @classmethod
    def load_from_json(cls, path: Path, /) -> Self:
        info: dict[str, Any] = {}

        if path.exists():
            try:
                info = cast('dict[str, Any]', json.loads(path.read_text()))
            except Exception:
                _logger.warning('Unable to read %s', path)

        if 'width' in info and 'height' in info:
            _logger.info('Bezel size read from %s', path)

        return cls(
            width=info.get('width'),
            height=info.get('height'),
            top=info.get('top'),
            bottom=info.get('bottom'),
            left=info.get('left'),
            right=info.get('right'),
            opacity=info.get('opacity'),
            message_x=info.get('messagex'),
            message_y=info.get('messagey'),
        )
