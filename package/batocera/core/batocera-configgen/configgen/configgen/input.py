from __future__ import annotations

from collections.abc import Mapping
from typing import TypeAlias


class Input:
    def __init__(self, name: str, type: str, id: str, value: str, code: str) -> None:
        self.name = name
        self.type = type
        self.id = id
        self.value = value
        self.code = code

InputMapping: TypeAlias = Mapping[str, Input]
InputDict: TypeAlias = dict[str, Input]
