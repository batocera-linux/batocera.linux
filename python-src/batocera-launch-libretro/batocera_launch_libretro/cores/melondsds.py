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
from batocera_launch_libretro import AssociatedMouseMixin, RACore

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class MelonDSDS(AssociatedMouseMixin, RACore):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # System Settings
        core_options.set_from_config('melonds_console_mode', 'melondsds_console_mode', default='ds')

        # Video Settings
        core_options.set_from_config('melonds_render_mode', 'melondsds_render_mode', default='software')
        core_options.set_from_config('melonds_opengl_resolution', 'melondsds_resolution', default='1')
        core_options.set_from_config('melonds_opengl_better_polygons', 'melondsds_poygon', default='disabled')
        core_options.set_from_config('melonds_opengl_filtering', 'melondsds_filtering', default='nearest')

        # Screen Settings
        core_options.set_from_config('melonds_show_cursor', 'melondsds_cursor', default='timeout')
        core_options.set_from_config('melonds_cursor_timeout', 'melondsds_cursor_timeout', default='3')
        core_options.set_from_config('melonds_touch_mode', 'melondsds_touchmode', default='auto')
        # set 1 screen for now top/botton
        core_options.set('melonds_number_of_screen_layouts', '1')
        core_options.set('melonds_screen_gap', '0')
        core_options.set('melonds_screen_layout1', 'top-bottom')

        # Firmware Settings
        core_options.set_from_config('melonds_firmware_wfc_dns', 'melondsds_dns', default='178.62.43.212')
        core_options.set_from_config('melonds_firmware_language', 'melondsds_language', default='default')
        core_options.set_from_config('melonds_firmware_favorite_color', 'melondsds_colour', default='default')
        core_options.set_from_config('melonds_firmware_birth_month', 'melondsds_month', default='default')
        core_options.set_from_config('melonds_firmware_birth_day', 'melondsds_day', default='default')

        # Onscreen Display
        core_options.set_from_config(
            'melonds_show_unsupported_features', 'melondsds_show_unsupported', default='disabled'
        )
        core_options.set_from_config('melonds_show_bios_warnings', 'melondsds_show_bios', default='disabled')
        core_options.set_from_config('melonds_show_current_layout', 'melondsds_show_layout', default='disabled')
        core_options.set_from_config('melonds_show_mic_state', 'melondsds_show_mic', default='disabled')
        core_options.set_from_config('melonds_show_camera_state', 'melondsds_show_camera', default='disabled')
        core_options.set_from_config('melonds_show_lid_state', 'melondsds_show_lid', default='disabled')
