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
class Ep128emuCore(Core):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Main thread wait (ms)
        core_options.set_from_config('ep128emu_wait', default='0')
        # High sound quality
        core_options.set_from_config('ep128emu_sdhq', default='1')
        # Use accelerated SW framebuffer
        core_options.set_from_config('ep128emu_swfb', default='0')
        # Enable resolution changes (requires restart)
        core_options.set_from_config('ep128emu_useh', default='1')
        # Border lines to keep when zooming in
        core_options.set_from_config('ep128emu_brds', default='0')
        # System ROM version (EP only)
        core_options.set_from_config('ep128emu_romv', default='Original')
        # User 1 Zoom button
        core_options.set_from_config('ep128emu_zoom', default='R3')
        # User 1 Info button
        core_options.set_from_config('ep128emu_info', default='L3')
        # User 1 Autofire for button
        core_options.set_from_config('ep128emu_afbt', default='None')
        # User 1 Autofire repeat delay
        core_options.set_from_config('ep128emu_afsp', default='2')
