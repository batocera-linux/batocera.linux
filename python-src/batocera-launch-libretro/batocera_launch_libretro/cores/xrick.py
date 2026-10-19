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

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import Core

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Xrick(Core):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Crop Borders
        core_options.set_bool_from_config('xrick_crop_borders', default=True, values=('enabled', 'disabled'))

        # Cheat 1 (Trainer Mode)
        core_options.set_bool_from_config('xrick_cheat1', values=('enabled', 'disabled'))

        # Cheat 2 (Invulnerablilty Mode)
        core_options.set_bool_from_config('xrick_cheat2', values=('enabled', 'disabled'))

        # Cheat 3 (Expose Mode)
        core_options.set_bool_from_config('xrick_cheat3', values=('enabled', 'disabled'))
