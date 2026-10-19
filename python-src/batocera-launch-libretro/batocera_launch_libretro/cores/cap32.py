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
from batocera_launch_libretro import RACore

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Cap32(RACore):
    @cached_property
    def player1_device_type(self) -> str | None:
        return '513'

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Virtual Keyboard by default (select+start) change to (start+Y)
        core_options.set('cap32_combokey', 'y')

        # Auto Select Model
        if self.system == 'gx4000':
            core_options.set('cap32_model', '6128+ (experimental)')
        else:
            model = self.config.get('cap32_model', '6128')
            core_options.set('cap32_model', '6128+ (experimental)' if model == '6128+' else model)

        # Ram size
        core_options.set_from_config('cap32_ram', default='128')

        # colour depth
        core_options.set_from_config('cap32_gfx_colors', 'cap32_colour', default='24bit')

        # language
        core_options.set_from_config('cap32_lang_layout', 'cap32_language', default='english')
