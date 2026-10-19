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

from typing import TYPE_CHECKING, ClassVar

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import RACore, SquashFSMixin

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class MesenS(SquashFSMixin, RACore):
    squashfs_rom_globs: ClassVar = {'satellaview': ('*.sfc', '*.smc')}
    gun_mapping: ClassVar = {'default': {'device': 262, 'p2': 0}}

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Force appropriate Game Boy mode for the system (unless overriden)
        gbmodel = self.config.get('mesen-s_gbmodel')
        if gbmodel is None:
            if self.system == 'sgb':
                gbmodel = 'Super Game Boy'
            elif self.system == 'gb':
                gbmodel = 'Game Boy'
            elif self.system == 'gbc':
                gbmodel = 'Game Boy Color'
            else:
                gbmodel = 'Auto'
        core_options.set('mesen-s_gbmodel', gbmodel)

        # SGB2 Enable (sgb only)
        if self.system == 'sgb':
            core_options.set_from_config('mesen-s_sgb2', default='enabled')

        # NTSC Filter
        core_options.set_from_config('mesen-s_ntsc_filter', default='Disabled')

        # Blending for high-res mode (Kirby's Dream Land 3 pseudo-transparency)
        core_options.set_from_config('mesen-s_blend_high_res', default='disabled')

        # Change sound interpolation to cubic
        core_options.set_from_config('mesen-s_cubic_interpolation', default='disabled')

        # SNES CPU Overclock
        core_options.set_from_config('mesen-s_overclock', default='None')

        # Overclocking type (compatibility)
        core_options.set_from_config('mesen-s_overclock_type', default='Before NMI')

        # SuperFX Overclock
        core_options.set_from_config('mesen-s_superfx_overclock', default='100%')
