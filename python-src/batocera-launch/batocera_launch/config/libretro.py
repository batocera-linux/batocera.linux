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

from dataclasses import InitVar, dataclass, field
from typing import TYPE_CHECKING

from batocera_common.key_value_config import KeyValueConfig

if TYPE_CHECKING:
    from pathlib import Path

    from .config import Config


@dataclass(slots=True)
class LibretroConfig:
    path: InitVar[Path]
    config: Config

    key_value_config: KeyValueConfig = field(init=False)

    def __post_init__(self, path: Path) -> None:
        self.key_value_config = KeyValueConfig(path, separator=' ')

    def write(self) -> None:
        self.key_value_config.write()

    def set(self, name: str, value: object, /) -> None:
        if value is None:
            value = ''
        elif isinstance(value, bool):
            value = 'true' if value else 'false'

        # RetroArch strips quotes for all values (0 is the same as "0") and determines value
        # type by the internal definition, not whether it is quoted or not. Quoting all
        # values ensures that RetroArch will always parse our generated files correctly
        # regardless of the kind of object we pass in.
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
