from __future__ import annotations

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class BK(Core):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Model: BK-0010, BK-0010.01, BK-0010.01 + FDD, BK-0011M + FDD, Terak 8510/a, Slow BK-0011M
        core_options.set_from_config('bk_model', default='BK-0011M + FDD')

        # Peripheral (UP port): none, covox, ay_3_8910, mouse_high, mouse_low, joystick
        core_options.set_from_config('bk_peripheral', default='none')

        # Double CPU speed: disabled, enabled
        core_options.set_from_config('bk_doublespeed', default='disabled')

        # Use color display: enabled, disabled
        core_options.set_from_config('bk_color', default='enabled')

        # Aspect ratio: 1:1, 4:3
        core_options.set_from_config('bk_aspect_ratio', default='1:1')

        # Keyboard layout: qwerty, jcuken
        core_options.set_from_config('bk_layout', default='qwerty')

        # Keyboard type: poll, callback
        core_options.set_from_config('bk_keyboard_type', default='poll')
