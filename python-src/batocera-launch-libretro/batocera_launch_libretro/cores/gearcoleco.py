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
from batocera_launch_libretro import RACore

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Gearcoleco(RACore):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Refresh Rate (requires restart)
        core_options.set_from_config('gearcoleco_timing', default='Auto')

        # Aspect Ratio
        core_options.set_from_config('gearcoleco_aspect_ratio', default='1:1 PAR')

        # Overscan
        core_options.set_from_config('gearcoleco_overscan', default='Disabled')

        # Allow Up+Down / Left+Right
        core_options.set_from_config('gearcoleco_up_down_allowed', default='Disabled')

        # No Sprite Limit
        core_options.set_from_config('gearcoleco_no_sprite_limit', default='Disabled')

        # Spinner support
        core_options.set_from_config('gearcoleco_spinners', default='Disabled')

        # Spinner Sensitivity
        core_options.set_from_config('gearcoleco_spinner_sensitivity', default='1')
