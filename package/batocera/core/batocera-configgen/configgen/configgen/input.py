from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING, Self, TypeAlias, cast

if TYPE_CHECKING:
    import xml.etree.ElementTree as ET


class Input:
    def __init__(self, name: str, type: str, id: str, value: str, code: str) -> None:
        self.name = name
        self.type = type
        self.id = id
        self.value = value
        self.code = code

    @classmethod
    def from_element(cls, element: ET.Element, /) -> Self:
        return cls(
            name=cast(str, element.get("name")),
            type=cast(str, element.get("type")),
            id=cast(str, element.get("id")),
            value=cast(str, element.get("value")),
            code=cast(str, element.get("code"))
        )

    @classmethod
    def from_parent_element(cls, parent_element: ET.Element, /) -> Iterator[tuple[str, Self]]:
        for element in parent_element.findall('input'):
            input = cls.from_element(element)
            yield input.name, input


InputMapping: TypeAlias = Mapping[str, Input]
InputDict: TypeAlias = dict[str, Input]
