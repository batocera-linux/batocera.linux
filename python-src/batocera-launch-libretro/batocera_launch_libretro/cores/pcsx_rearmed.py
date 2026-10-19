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
    from batocera_launch import Controller, Gun, LibretroConfig


@cached_dataclass
class PcsxRearmed(RACore):
    gun_mapping: ClassVar = {
        'default': {
            'device': 260,
            'p1': 0,
            'p2': 1,
            'gameDependant': [{'key': 'type', 'value': 'justifier', 'mapkey': 'device', 'mapvalue': '516'}],
        }
    }

    @cached_property
    def player1_device_type(self) -> str | None:
        return self.config.get_str('controller1_pcsx') or None

    @cached_property
    def player2_device_type(self) -> str | None:
        return self.config.get_str('controller2_pcsx') or None

    def get_analog_mode(self, controller: Controller, /) -> Literal['0', '1']:
        if controller.player_number == 1 and (psx_controller_1 := self.config.get('controller1_pcsx')):
            return '0' if psx_controller_1 != '1' else '1'

        if controller.player_number == 2 and (psx_controller_2 := self.config.get('controller2_pcsx')):
            return '0' if psx_controller_2 != '1' else '1'

        return super().get_analog_mode(controller)

    def set_config(self, custom_config: LibretroConfig, /) -> None:
        super().set_config(custom_config)

        # wheel
        if self.config.use_wheels:
            for pad in self.controllers:
                if pad.device_path in self.wheels:
                    custom_config.set(f'input_player{pad.player_number}_analog_dpad_mode', '1')
                    if self.metadata.get('wheel_type') == 'negcon':
                        custom_config.set(f'input_libretro_device_p{pad.player_number}', 773)  # Negcon
                    else:
                        custom_config.set(f'input_libretro_device_p{pad.player_number}', 517)  # DualShock Controller

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Display Multitap/Gamepad Options
        core_options.set('pcsx_rearmed_show_input_settings', 'enabled')

        # Enable Vibration
        core_options.set('pcsx_rearmed_vibration', 'enabled')

        # Show Bios Bootlogo (Breaks some games)
        core_options.set_from_config('pcsx_rearmed_show_bios_bootlogo', 'show_bios_bootlogo', default='disabled')

        # Frameskip
        frameskip = self.config.get_str('frameskip_pcsx', '0')
        if frameskip == '0':
            core_options.set('pcsx_rearmed_frameskip_type', 'disabled')
        else:
            core_options.set('pcsx_rearmed_frameskip_type', 'fixed_interval')
            core_options.set('pcsx_rearmed_frameskip_interval', frameskip)

        # Enhanced resolution at the cost of lower performance
        match self.config.get('neon_enhancement'):
            case 'enabled':
                core_options.set('pcsx_rearmed_neon_enhancement_enable', 'enabled')
                core_options.set('pcsx_rearmed_neon_enhancement_no_main', 'disabled')
            case 'enabled_with_speedhack':
                core_options.set('pcsx_rearmed_neon_enhancement_enable', 'enabled')
                core_options.set('pcsx_rearmed_neon_enhancement_no_main', 'enabled')
            case _:
                core_options.set('pcsx_rearmed_neon_enhancement_enable', 'disabled')
                core_options.set('pcsx_rearmed_neon_enhancement_no_main', 'disabled')

        # Multitap
        core_options.set_from_config('pcsx_rearmed_multitap', 'pcsx_rearmed_multitap', default='disabled')

        # gun cross
        # Crossbar Colors
        need_crosses = self.emulator.guns_need_crosses
        for player, color in enumerate(['red', 'blue'], start=1):
            core_options.set_from_config(
                f'pcsx_rearmed_crosshair{player}',
                f'pcsx_rearmed_crosshair{player}',
                default=color if need_crosses else 'disabled',
            )

    def get_pedal_config_name_for_player(self, player_number: int, /) -> str:
        return f'input_player{player_number}_gun_aux_a'

    def set_gun_config_for_player(self, custom_config: LibretroConfig, player_number: int, gun: Gun, /) -> None:
        if self.metadata.get('gun_type') == 'justifier':
            custom_config.set(f'input_player{player_number}_gun_offscreen_shot_mbtn', '')
            custom_config.set(f'input_player{player_number}_gun_aux_a_mbtn', 2)
        else:
            custom_config.set(f'input_player{player_number}_gun_offscreen_shot_mbtn', '')
            custom_config.set(f'input_player{player_number}_gun_start_mbtn', '')
            custom_config.set(f'input_player{player_number}_gun_aux_a_mbtn', 2)
            custom_config.set(f'input_player{player_number}_gun_aux_b_mbtn', 3)
