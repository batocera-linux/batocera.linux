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
class Dice(Core):
    def set_config(self, custom_config: LibretroConfig, /) -> None:
        super().set_config(custom_config)

        custom_config.set('input_player1_select', 'num5')

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Pointer-as-paddle, simplest mouse setup
        core_options.set_from_config(
            'dice_use_mouse_pointer_for_paddle_1', 'ttl_use_mouse_pointer_for_paddle_1', default='disabled'
        )
        # DEVICE_RETRO_MOUSE control of paddles
        core_options.set_from_config('dice_retromouse_paddle0', 'ttl_retromouse_paddle0', default='disabled')
        core_options.set_from_config('dice_retromouse_paddle1', 'ttl_retromouse_paddle1', default='disabled')
        core_options.set_from_config('dice_retromouse_paddle2', 'ttl_retromouse_paddle2', default='disabled')
        core_options.set_from_config('dice_retromouse_paddle3', 'ttl_retromouse_paddle3', default='disabled')
        # Axes for mouse-paddles.  Default for mice, but allow overrides for spinner setups
        core_options.set_from_config('dice_retromouse_paddle0_x', 'ttl_retromouse_paddle0_x', default='x')
        core_options.set_from_config('dice_retromouse_paddle0_y', 'ttl_retromouse_paddle0_y', default='y')
        core_options.set_from_config('dice_retromouse_paddle1_x', 'ttl_retromouse_paddle1_x', default='x')
        core_options.set_from_config('dice_retromouse_paddle1_y', 'ttl_retromouse_paddle1_y', default='y')
        core_options.set_from_config('dice_retromouse_paddle2_x', 'ttl_retromouse_paddle2_x', default='x')
        core_options.set_from_config('dice_retromouse_paddle2_y', 'ttl_retromouse_paddle2_y', default='y')
        core_options.set_from_config('dice_retromouse_paddle3_x', 'ttl_retromouse_paddle3_x', default='x')
        core_options.set_from_config('dice_retromouse_paddle3_y', 'ttl_retromouse_paddle3_y', default='y')
        # Miscellaneous input scaling tweaks
        core_options.set_from_config(
            'dice_paddle_keyboard_sensitivity', 'ttl_paddle_keyboard_sensitivity', default='250'
        )
        core_options.set_from_config(
            'dice_paddle_joystick_sensitivity', 'ttl_paddle_joystick_sensitivity', default='500'
        )
        core_options.set_from_config(
            'dice_retromouse_paddle_sensitivity', 'ttl_retromouse_paddle_sensitivity', default='125'
        )
        core_options.set_from_config('dice_wheel_keyjoy_sensitivity', 'ttl_wheel_keyjoy_sensitivity', default='500')
        core_options.set_from_config(
            'dice_throttle_keyjoy_sensitivity', 'ttl_throttle_keyjoy_sensitivity', default='250'
        )
        # DIP switches
        core_options.set_from_config('dice_dipswitch_1', 'ttl_dipswitch_1', default='-1')
        core_options.set_from_config('dice_dipswitch_2', 'ttl_dipswitch_2', default='-1')
        core_options.set_from_config('dice_dipswitch_3', 'ttl_dipswitch_3', default='-1')
        core_options.set_from_config('dice_dipswitch16_1', 'ttl_dipswitch16_1', default='-1')
        core_options.set_from_config('dice_dipswitch16_2', 'ttl_dipswitch16_2', default='-1')
