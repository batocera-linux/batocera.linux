from __future__ import annotations

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, DisableRewindMixin, DisableRunaheadMixin, LibretroConfig


@cached_dataclass
class Dice(DisableRewindMixin, DisableRunaheadMixin, Core):
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
        core_options.set_from_config('dice_retromouse_paddle1_x', 'ttl_retromouse_paddle0_x', default='x')
        core_options.set_from_config('dice_retromouse_paddle1_y', 'ttl_retromouse_paddle0_y', default='y')
        core_options.set_from_config('dice_retromouse_paddle2_x', 'ttl_retromouse_paddle0_x', default='x')
        core_options.set_from_config('dice_retromouse_paddle2_y', 'ttl_retromouse_paddle0_y', default='y')
        core_options.set_from_config('dice_retromouse_paddle3_x', 'ttl_retromouse_paddle0_x', default='x')
        core_options.set_from_config('dice_retromouse_paddle3_y', 'ttl_retromouse_paddle0_y', default='y')
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
