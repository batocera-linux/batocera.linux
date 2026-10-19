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

from .vice_x64 import jiffydos_option

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class ViceX128(Core):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Activate Jiffydos
        core_options.set('vice_jiffydos', jiffydos_option('JiffyDOS_C64.bin', 'JiffyDOS_C128.bin'))
        # Enable Automatic Load Warp
        core_options.set('vice_autoloadwarp', 'enabled')
        # Disable Datasette Hotkeys
        core_options.set('vice_datasette_hotkeys', 'disabled')
        # Not Read 'vicerc'
        core_options.set('vice_read_vicerc', 'disabled')
        # Select Joystick Type
        core_options.set('vice_Controller', 'joystick')
        # Disable Turbo Fire
        core_options.set('vice_turbo_fire', 'disabled')

        # Model type
        core_options.set_from_config('vice_c128_model', 'c128_model', default='C128 PAL')

        # Aspect Ratio
        core_options.set_from_config('vice_aspect_ratio', default='pal')

        # Zoom Mode
        zoom_mode = self.config.get('vice_zoom_mode', 'auto_disable')
        core_options.set('vice_crop', 'auto' if zoom_mode == 'automatic' else zoom_mode)
        core_options.set('vice_zoom_mode', 'deprecated')

        # External palette
        core_options.set_from_config('vice_external_palette', default='colodore')

        # Button options
        core_options.set_from_config('vice_retropad_options', default='disabled')

        # Select Controller Port
        core_options.set_from_config('vice_joyport', default='2')

        # Select Controller Type
        core_options.set_from_config('vice_joyport_type', default='1')

        # RAM Expansion Unit
        core_options.set_from_config('vice_c128_ram_expansion_unit', default='none')

        # Keyboard Pass-through for Pad2Key
        core_options.set_from_config(
            'vice_physical_keyboard_pass_through', 'vice_keyboard_pass_through', default='disabled'
        )
