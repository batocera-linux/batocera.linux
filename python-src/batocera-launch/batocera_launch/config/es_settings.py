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
        try:
            document = ET.parse(ES_SETTINGS)
        except Exception:
            document = ET.ElementTree[ET.Element[str]](ET.Element('config'))

        return cls(document=document)
