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

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import ROMS
from batocera_launch_libretro import Core

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class Vitaquake2(Core):
    @cached_property
    def _mission(self) -> tuple[str, Path]:
        # vitaquake2 - choose core based on directory
        name = self.config.rom.name.lower()

        if 'reckoning' in name:
            return 'vitaquake2-xatrix', ROMS / 'quake2' / 'xatrix' / 'pak0.pak'

        if 'zero' in name:
            return 'vitaquake2-rogue', ROMS / 'quake2' / 'rogue' / 'pak0.pak'

        if 'zaero' in name:
            return 'vitaquake2-zaero', ROMS / 'quake2' / 'zaero' / 'pak0.pak'

        return self.emulator.core, ROMS / 'quake2' / 'baseq2' / 'pak0.pak'

    @cached_property
    def library_prefix(self) -> str:
        return self._mission[0]

    @cached_property
    def rom_argument(self) -> str | Path | None:
        return self._mission[1]
