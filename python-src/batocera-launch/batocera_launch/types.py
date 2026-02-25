from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(slots=True, frozen=True)
class Resolution:
    width: int
    height: int


class HotkeysContext(TypedDict):
    name: str
    keys: dict[str, Sequence[str]]  # Sequence[str] covers both str and list[str]
