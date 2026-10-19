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
from batocera_common.paths import BIOS, ROMS
from batocera_launch_libretro import Core

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Px68k(Core):
    def generate_special_configs(self) -> None:
        # Fresh config file
        keropi_config = BIOS / 'keropi' / 'config'
        keropi_sram = BIOS / 'keropi' / 'sram.dat'
        for f in [keropi_config, keropi_sram]:
            if f.exists():
                f.unlink()
        with keropi_config.open('w') as fd:
            fd.write('[WinX68k]\n')
            fd.write(f'StartDir={ROMS / "x68000"}\n')

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # CPU Speed (Overclock)
        cpuspeed = self.config.get('px68k_cpuspeed', '33Mhz (OC)')
        core_options.set('px68k_cpuspeed', '100Mhz (OC)' if cpuspeed in {'150Mhz (OC)', '200Mhz (OC)'} else cpuspeed)

        # RAM Size
        core_options.set_from_config('px68k_ramsize', default='12MB')

        # Frame Skip
        frameskip = self.config.get('px68k_frameskip', 'Full Frame')
        core_options.set(
            'px68k_frameskip', {'1/8 Frame1': '1/8 Frame', '16 Frame': '1/16 Frame'}.get(frameskip, frameskip)
        )

        # Joypad Type for two players
        joytype = self.config.get('px68k_joytype', 'Default (2 Buttons)')
        core_options.set('px68k_joytype1', joytype)
        core_options.set('px68k_joytype2', joytype)
