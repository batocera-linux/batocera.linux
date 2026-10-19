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
class ViceXpet(Core):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
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
        core_options.set_from_config('vice_pet_model', 'pet_model', default='8032')

        # Zoom Mode
        zoom_mode = self.config.get('vice_zoom_mode', 'auto_disable')
        core_options.set('vice_crop', 'auto' if zoom_mode == 'automatic' else zoom_mode)
        core_options.set('vice_zoom_mode', 'deprecated')

        # External palette
        core_options.set_from_config('vice_pet_external_palette', default='default')

        # Keyboard Pass-through for Pad2Key
        core_options.set_from_config(
            'vice_physical_keyboard_pass_through', 'vice_keyboard_pass_through', default='disabled'
        )
