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
class O2em(RACore):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Virtual keyboard transparency
        core_options.set('o2em_vkbd_transparency', '25')

        # Emulated Hardware
        core_options.set_from_config('o2em_bios', default='g7400.bin' if self.system == 'videopacplus' else 'o2rom.bin')

        # Emulated Hardware
        region = self.config.get('o2em_region', 'autodetect')
        core_options.set('o2em_region', 'auto' if region == 'autodetect' else region)

        # Swap Gamepad
        core_options.set_from_config('o2em_swap_gamepads', default='disabled')

        # Crop Overscan
        core_options.set_from_config('o2em_crop_overscan', default='enabled')

        # Ghosting effect
        core_options.set_from_config('o2em_mix_frames', default='disabled')

        # Audio Filter
        low_pass_range = self.config.get('o2em_low_pass_range', '0')
        core_options.set('o2em_low_pass_filter', 'disabled' if low_pass_range == '0' else 'enabled')
        core_options.set('o2em_low_pass_range', low_pass_range)
