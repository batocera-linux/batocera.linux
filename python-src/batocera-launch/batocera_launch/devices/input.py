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

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Self, TypedDict, Unpack, cast

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
    code: str | None = None

    def replace(self, /, **changes: Unpack[_InputChanges]) -> Self:
        return replace(self, **changes)

    @classmethod
    def from_element(cls, element: ET.Element, /) -> Self:
        return cls(
            name=cast('str', element.get('name')),
            type=cast('str', element.get('type')),
            id=cast('str', element.get('id')),
            value=cast('str', element.get('value')),
            code=element.get('code'),
        )

    @classmethod
    def from_parent_element(cls, parent_element: ET.Element, /) -> Iterator[tuple[str, Self]]:
        for element in parent_element.iterfind('./input'):
            input = cls.from_element(element)
            yield input.name, input


type InputMapping = Mapping[str, Input]
type InputDict = dict[str, Input]
