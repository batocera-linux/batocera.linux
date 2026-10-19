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

from pathlib import Path
from typing import Final

from batocera_common.paths import BIOS, CHEATS, CONFIGS, ROMS, SAVES
from batocera_launch.paths import LAUNCH_DATA_DIR

MAME_BIN_DIR: Final = Path('/usr/bin/mame')
MAME_DATA_DIR: Final = LAUNCH_DATA_DIR / 'mame'


class MAMEPathsMixin:
    @property
    def roms_dir(self) -> Path:
        return ROMS / 'mame'

    @property
    def bios_dir(self) -> Path:
        return BIOS / 'mame'

    @property
    def config_dir(self) -> Path:
        return CONFIGS / 'mame'

    @property
    def saves_dir(self) -> Path:
        return SAVES / 'mame'

    @property
    def cheats_dir(self) -> Path:
        return CHEATS / 'mame'
