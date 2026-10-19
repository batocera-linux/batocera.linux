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

from typing import TYPE_CHECKING, ClassVar, Literal

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch_libretro import RACore

if TYPE_CHECKING:
    from batocera_launch import Controller, LibretroConfig


@cached_dataclass
class MednafenPsx(RACore):
    gun_mapping: ClassVar = {'default': {'device': 260, 'p1': 0, 'p2': 1}}

    @cached_property
    def player1_device_type(self) -> str | None:
        return self.config.get_str('beetle_psx_hw_Controller1') or None

    @cached_property
    def player2_device_type(self) -> str | None:
        return self.config.get_str('beetle_psx_hw_Controller2') or None

    def get_analog_mode(self, controller: Controller, /) -> Literal['0', '1']:
        if controller.player_number == 1 and (psx_controller_1 := self.config.get('beetle_psx_hw_Controller1')):
            return '0' if psx_controller_1 != '1' else '1'

        if controller.player_number == 2 and (psx_controller_2 := self.config.get('beetle_psx_hw_Controller2')):
            return '0' if psx_controller_2 != '1' else '1'

        return super().get_analog_mode(controller)

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # the software-only build reads the same options without the _hw prefix
        def set_option(name: str, value: object, /) -> None:
            core_options.set(f'beetle_psx_hw_{name}', value)
            core_options.set(f'beetle_psx_{name}', value)

        def set_option_from_config(name: str, /, *, default: object) -> None:
            set_option(name, self.config.get(f'beetle_psx_hw_{name}', default))

        # CPU Frequency Scaling (Overclock)
        set_option_from_config('cpu_freq_scale', default='100%')

        # Show official Bootlogo
        set_option_from_config('skip_bios', default='disabled')

        # Video Resolution
        set_option_from_config('internal_resolution', default='1x(native)')

        # Widescreen Hack
        if (
            self.config.get('beetle_psx_hw_widescreen_hack') == 'enabled'
            and self.config.get('ratio') == '16/9'
            and self.config.get('bezel') == 'none'
        ):
            set_option('widescreen_hack', 'enabled')
        else:
            set_option('widescreen_hack', 'disabled')

        # Frame Duping (Speedup)
        set_option_from_config('frame_duping', default='disabled')

        # CPU Dynarec (Speedup)
        set_option_from_config('cpu_dynarec', default='disabled')

        # Dynarec Code Invalidation
        set_option_from_config('dynarec_invalidate', default='full')

        set_option_from_config('pgxp_mode', default='disabled')

        # Analog Stick self calibration
        set_option('analog_calibration', 'enabled')

        # Multitap
        match self.config.get('multitap_mednafen'):
            case 'port1':
                set_option('enable_multitap_port1', 'enabled')
                set_option('enable_multitap_port2', 'disabled')
            case 'port2':
                set_option('enable_multitap_port1', 'disabled')
                set_option('enable_multitap_port2', 'enabled')
            case 'port12':
                set_option('enable_multitap_port1', 'enabled')
                set_option('enable_multitap_port2', 'enabled')
            case _:
                set_option('enable_multitap_port1', 'disabled')
                set_option('enable_multitap_port2', 'disabled')
