from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from batocera_launch import KeyValueConfig, SystemConfig

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(slots=True)
class LibretroConfig:
    key_value_config: KeyValueConfig = field(init=False)
    config: SystemConfig
    path: Path

    def __post_init__(self) -> None:
        self.key_value_config = KeyValueConfig(' ')
        self.key_value_config.read(self.path)

    def write(self) -> None:
        self.key_value_config.write(self.path)

    def set(self, name: str, value: object, /) -> None:
        if value is None:
            value = ''
        elif isinstance(value, bool):
            value = 'true' if value else 'false'

        self.key_value_config[name] = f'"{value}"'

    def set_from_config(self, name: str, config_name: str | None = None, /, *, default: object = None) -> None:
        self.set(name, self.config.get(config_name or name, default))

    def set_bool_from_config(
        self,
        name: str,
        config_name: str | None = None,
        /,
        *,
        default: bool = False,
        values: tuple[object, object] | None = None,
    ) -> None:
        self.set(name, self.config.get_bool(config_name or name, default, return_values=values))

    def set_int_from_config(self, name: str, config_name: str | None = None, /, *, default: int | None = None) -> None:
        self.set(name, self.config.get_int(config_name or name, default))

    def set_float_from_config(
        self, name: str, config_name: str | None = None, /, *, default: float | None = None
    ) -> None:
        self.set(name, self.config.get_float(config_name or name, default))

    def remove_section(self, section: str, /) -> None:
        self.key_value_config.remove_section(section)

    def remove_all_starting_with(self, prefix: str, /) -> None:
        self.key_value_config.remove_all_starting_with(prefix)
