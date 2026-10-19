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
class Mgba(RACore):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Skip BIOS intro
        core_options.set_bool_from_config('mgba_skip_bios', 'skip_bios_mgba', values=('ON', 'OFF'))

        # Rumble
        # This works because only '1' is treated as True in get_bool()
        core_options.set_bool_from_config('mgba_force_gbp', 'rumble_gain', default=True, values=('OFF', 'ON'))

        if self.system == 'gba':
            # GBA: Solar sensor level, Boktai 1: The Sun is in Your Hand
            core_options.set_from_config('mgba_solar_sensor_level', 'solar_sensor_level', default='0')

            # GBA: Frameskip
            core_options.set_from_config('mgba_frameskip', 'frameskip_mgba', default='0')

        # Force Super Game Boy mode for SGB system, auto for all others
        # No current option to override - add if needed.
        if self.system == 'sgb':
            core_options.set('mgba_gb_model', 'Super Game Boy')

            # Default border to on for SGB
            core_options.set_bool_from_config('mgba_sgb_borders', 'sgb_borders', default=True, values=('ON', 'OFF'))
        else:
            core_options.set('mgba_gb_model', 'Autodetect')
