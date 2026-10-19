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
from batocera_launch_libretro import AssociatedMouseMixin, GLCoreOverrideMixin, RACore

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class MelonDS(AssociatedMouseMixin, GLCoreOverrideMixin, RACore):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Console Mode
        core_options.set_from_config('melonds_console_mode', default='DS')

        # Language
        core_options.set_from_config('melonds_language', default='English')

        # External Firmware
        core_options.set_from_config('melonds_use_fw_settings', default='disabled')

        # Enable threaded rendering
        core_options.set('melonds_threaded_renderer', 'enabled')

        # Emulate Stylus on Right Stick
        core_options.set_from_config('melonds_touch_mode', default='Joystick')

        # Boot game directly
        core_options.set_from_config('melonds_boot_directly', default='enabled')

        # Screen Layout + Hybrid Ratio
        hybrid_ratio = '2'
        core_options.set('melonds_hybrid_ratio', '2')

        match self.config.get('melonds_screen_layout', 'Top/Bottom'):
            case 'Hybrid Top-Ratio2':
                layout = 'Hybrid Top'
            case 'Hybrid Top-Ratio3':
                layout = 'Hybrid Top'
                hybrid_ratio = '3'
            case 'Hybrid Bottom-Ratio2':
                layout = 'Hybrid Bottom'
            case 'Hybrid Bottom-Ratio3':
                layout = 'Hybrid Bottom'
                hybrid_ratio = '3'
            case _ as screen_layout:
                layout = screen_layout

        core_options.set('melonds_screen_layout', layout)
        core_options.set('melonds_hybrid_ratio', hybrid_ratio)
