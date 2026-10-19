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

import tomllib
from dataclasses import dataclass
from typing import Self

from .paths import MAME_DATA_DIR


@dataclass(slots=True)
class MessSystemInfo:
    name: str
    rom_type: str
    auto_run: str | None

    @classmethod
    def load(cls, system_name: str, /) -> Self | None:
        mess_systems = tomllib.loads(MAME_DATA_DIR.joinpath('mess_systems.toml').read_text())
        mess_system = mess_systems.get(system_name, None)

        # This must be an `is not None` check because the dictionary could be empty
        if mess_system is not None:
            return cls(
                mess_system.get('name', system_name),
                mess_system.get('rom_type', ''),
                mess_system.get('auto_run'),
            )

        return None
