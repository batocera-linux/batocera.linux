from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class Stella(Core):
    supports_retroachievements: ClassVar = True
    gun_mapping: ClassVar = {'default': {'device': 4, 'p1': 0, 'p2': 1}}

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Video standard / console type
        core_options.set_from_config('stella_console', default='auto')

        # Palette / colors
        core_options.set_from_config('stella_palette', default='standard')

        # TV effects / filter
        core_options.set_from_config('stella_filter', default='disabled')

        # Overscan cropping
        core_options.set_from_config('stella_crop_hoverscan', default='disabled')
        core_options.set_from_config('stella_crop_voverscan', default='0')

        # Aspect ratio correction (percent). "par" = pixel aspect ratio
        core_options.set_from_config('stella_ntsc_aspect', default='par')
        core_options.set_from_config('stella_pal_aspect', default='par')

        # Audio
        core_options.set_from_config('stella_stereo', default='auto')

        # Phosphor (motion blur)
        core_options.set_from_config('stella_phosphor', default='auto')
        core_options.set_from_config('stella_phosphor_blend', default='60')

        # Paddles
        core_options.set_from_config('stella_paddle_mouse_sensitivity', default='10')
        core_options.set_from_config('stella_paddle_joypad_sensitivity', default='3')
        core_options.set_from_config('stella_paddle_analog_sensitivity', default='20')
        core_options.set_from_config('stella_paddle_analog_deadzone', default='15')
        core_options.set_from_config('stella_paddle_analog_absolute', default='disabled')

        # Lightgun crosshair
        core_options.set_from_config(
            'stella_lightgun_crosshair',
            default='enabled' if self.emulator.guns_need_crosses else 'disabled',
        )

        # Convenience
        core_options.set_from_config('stella_reload', default='off')
