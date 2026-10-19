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
from batocera_launch_libretro import RACore

from ._snes9x_core import Snes9xControllersMixin

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Snes9xNext(Snes9xControllersMixin, RACore):
    gun_mapping: ClassVar = {
        'default': {
            'device': 260,
            'p2': 0,
            'gameDependant': [{'key': 'type', 'value': 'justifier', 'mapkey': 'device', 'mapvalue': '516'}],
        }
    }

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Reduce sprite flickering (Hack, Unsafe)
        core_options.set_from_config(
            'snes9x_2010_reduce_sprite_flicker', '2010_reduce_sprite_flicker', default='enabled'
        )

        # Reduce Slowdown (Hack, Unsafe)
        core_options.set_from_config('snes9x_2010_overclock_cycles', '2010_reduce_slowdown', default='disabled')

        # SuperFX Overclocking
        core_options.set_from_config('snes9x_2010_overclock', '2010_overclock_superfx', default='10 MHz (Default)')

        # Blargg NTSC Filter
        core_options.set_from_config('snes9x_2010_blargg', 'snes9x_2010_blargg_filter', default='disabled')
