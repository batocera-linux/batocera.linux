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
    def set_config(self, custom_config: LibretroConfig, /) -> None:
        for pad in self.controllers[:4]:
            for btn, value in _ANYBOR_REMAP_VALUES.items():
                custom_config.set(f'input_player{pad.player_number}_{btn}', value)
