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

import xml.etree.ElementTree as ET
from dataclasses import dataclass

from ..paths import ES_SETTINGS


@dataclass(slots=True)
class ESSettings:
    document: ET.ElementTree[ET.Element[str]]

    def __get_value(self, key: str, type: str, /) -> str | None:
        node = self.document.find(f'./{type}[@name="{key}"]')

        if node is None:
            return None

        return node.attrib['value']

    def get_bool(self, key: str, /, default: bool = False) -> bool:
        value = self.__get_value(key, 'bool')

        if value not in {'false', 'true'}:
            return default

        return value == 'true'

    def get_str(self, key: str, /, default: str | None = None) -> str | None:
        value = self.__get_value(key, 'string')

        if value is None:
            return default

        return value

    def get_int(self, key: str, /, default: int | None = None) -> int | None:
        value = self.__get_value(key, 'int')

        if value is None:
            return default

        return int(value)

    @classmethod
    def load(cls) -> ESSettings:
        document: ET.ElementTree[ET.Element[str]]
        try:
            document = ET.parse(ES_SETTINGS)
        except Exception:
            document = ET.ElementTree(ET.Element('config'))

        return cls(document=document)
