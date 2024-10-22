from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Self, TypeAlias, TypedDict, Unpack, cast

if TYPE_CHECKING:
    import xml.etree.ElementTree as ET


class _InputChanges(TypedDict, total=False):
    name: str
    type: str
    id: str
    value: str
    code: str | None


@dataclass(slots=True, kw_only=True)
class Input:
    name: str
    type: str
    id: str
    value: str
    code: str | None

    def replace(self, /, **changes: Unpack[_InputChanges]) -> Self:
        return replace(self, **changes)

    @classmethod
    def from_element(cls, element: ET.Element, /) -> Self:
        return cls(
            name=cast(str, element.get("name")),
            type=cast(str, element.get("type")),
            id=cast(str, element.get("id")),
            value=cast(str, element.get("value")),
            code=element.get("code")
        )

    @classmethod
    def from_parent_element(cls, parent_element: ET.Element, /) -> Iterator[tuple[str, Self]]:
        for element in parent_element.findall('input'):
            input = cls.from_element(element)
            yield input.name, input


InputMapping: TypeAlias = Mapping[str, Input]
InputDict: TypeAlias = dict[str, Input]
