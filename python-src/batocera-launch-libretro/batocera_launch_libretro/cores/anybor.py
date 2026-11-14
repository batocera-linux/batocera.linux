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

from typing import TYPE_CHECKING, Final

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import RACore

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig

# The core reads attack on Y, jump on B and special on A; keep the standalone OpenBOR layout
_ANYBOR_REMAP_VALUES: Final = {
    'btn_b': '1',
    'btn_a': '0',
    'btn_y': '8',
}


@cached_dataclass
class AnyBOR(RACore):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # RetroArch's CRT SwitchRes is on for CRT output (the Batocera CRT Script sets
        # global.retroarch.crt_switch_resolution); fit the image to a 4:3 TV there
        crt = self.config.get_str('retroarch.crt_switch_resolution', '0') not in ('', '0')
        core_options.set('anybor_crt_tv', 'On' if crt else 'Off')

    def set_config(self, custom_config: LibretroConfig, /) -> None:
        for pad in self.controllers[:4]:
            for btn, value in _ANYBOR_REMAP_VALUES.items():
                custom_config.set(f'input_player{pad.player_number}_{btn}', value)

        # Rewind: a snapshot every 10 frames, into a 256 MB buffer
        custom_config.set('rewind_granularity', 10)
        custom_config.set('rewind_buffer_size', 256)
