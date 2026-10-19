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
class BK(Core):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Model: BK-0010, BK-0010.01, BK-0010.01 + FDD, BK-0011M + FDD, Terak 8510/a, Slow BK-0011M
        core_options.set_from_config('bk_model', default='BK-0011M + FDD')

        # Peripheral (UP port): none, covox, ay_3_8910, mouse_high, mouse_low, joystick
        core_options.set_from_config('bk_peripheral', default='none')

        # Double CPU speed: disabled, enabled
        core_options.set_from_config('bk_doublespeed', default='disabled')

        # Use color display: enabled, disabled
        core_options.set_from_config('bk_color', default='enabled')

        # Aspect ratio: 1:1, 4:3
        core_options.set_from_config('bk_aspect_ratio', default='1:1')

        # Keyboard layout: qwerty, jcuken
        core_options.set_from_config('bk_layout', default='qwerty')

        # Keyboard type: poll, callback
        core_options.set_from_config('bk_keyboard_type', default='poll')
