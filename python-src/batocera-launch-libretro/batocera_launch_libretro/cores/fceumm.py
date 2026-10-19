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

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch_libretro import RACore

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Fceumm(RACore):
    gun_mapping: ClassVar = {'default': {'device': 258, 'p2': 0}}

    @cached_property
    def player1_device_type(self) -> str | None:
        return self.config.get_str('controller1_nes', '1')

    @cached_property
    def player2_device_type(self) -> str | None:
        return self.config.get_str('controller2_nes', '1')

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # gun
        core_options.set(
            'fceumm_zapper_mode', 'clightgun' if self.config.use_guns and self.guns else 'mouse'
        )  # FCEumm Mouse mode for Zapper

        # gun cross
        core_options.set_from_config(
            'fceumm_show_crosshair',
            default='enabled' if self.emulator.guns_need_crosses else 'disabled',
        )

        # Reduce Sprite Flickering
        core_options.set_from_config('fceumm_nospritelimit', default='enabled')

        # Crop Overscan
        match self.config.get('fceumm_cropoverscan'):
            case 'none':
                overscan_h = '0'
                overscan_v = '0'
            case 'h':
                overscan_h = '8'
                overscan_v = '0'
            case 'both':
                overscan_h = '8'
                overscan_v = '8'
            case _:
                overscan_h = '0'
                overscan_v = '8'
        core_options.set('fceumm_overscan_h_left', overscan_h)
        core_options.set('fceumm_overscan_h_right', overscan_h)
        core_options.set('fceumm_overscan_v_top', overscan_v)
        core_options.set('fceumm_overscan_v_bottom', overscan_v)

        # Palette Choice
        palette = self.config.get('fceumm_palette', 'default')
        core_options.set('fceumm_palette', 'wii-vc' if palette == 'nintendo-vc' else palette)

        # NTSC Filter
        core_options.set_from_config('fceumm_ntsc_filter', default='disabled')

        # Sound Quality
        core_options.set_from_config('fceumm_sndquality', default='Low')

        # PPU Overclocking
        core_options.set_from_config('fceumm_overclocking', default='disabled')
