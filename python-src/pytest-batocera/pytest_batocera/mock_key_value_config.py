from __future__ import annotations

from configparser import UNNAMED_SECTION
from dataclasses import InitVar, dataclass, field
from typing import TYPE_CHECKING, cast

from batocera_common.key_value_config import KeyValueConfig

if TYPE_CHECKING:
    from batocera_common.configparser import CaseSensitiveConfigParser


@dataclass(slots=True)
class MockKeyValueConfig(KeyValueConfig):
    data: InitVar[dict[str, str]] = field(kw_only=True)

    def __post_init__(self, data: dict[str, str]) -> None:
        super().__post_init__()

        config = cast('CaseSensitiveConfigParser', self._KeyValueConfig__config)  # pyright: ignore
        config.read_dict({UNNAMED_SECTION: data})  # pyright: ignore[reportArgumentType]
