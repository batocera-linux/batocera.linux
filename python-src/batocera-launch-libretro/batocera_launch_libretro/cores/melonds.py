from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import AssociatedMouseMixin, Core, GLCoreOverrideMixin, LibretroConfig


@cached_dataclass
class MelonDS(AssociatedMouseMixin, GLCoreOverrideMixin, Core):
    supports_retroachievements: ClassVar = True

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Console Mode
        core_options.set_from_config('melonds_console_mode', default='DS')

        # Language
        core_options.set_from_config('melonds_language', default='English')

        # External Firmware
        core_options.set_from_config('melonds_use_fw_settings', default='disable')

        # Enable threaded rendering
        core_options.set('melonds_threaded_renderer', 'enabled')

        # Emulate Stylus on Right Stick
        core_options.set_from_config('melonds_touch_mode', default='Joystick')

        # Boot game directly
        core_options.set_from_config('melonds_boot_directly', default='enabled')

        # Screen Layout + Hybrid Ratio
        hybrid_ratio = '2'
        core_options.set('melonds_hybrid_ratio', '2')

        match self.config.get('melonds_screen_layout', 'Top/Bottom'):
            case 'Hybrid Top-Ratio2':
                layout = 'Hybrid Top'
            case 'Hybrid Top-Ratio3':
                layout = 'Hybrid Top'
                hybrid_ratio = '3'
            case 'Hybrid Bottom-Ratio2':
                layout = 'Hybrid Bottom'
            case 'Hybrid Bottom-Ratio3':
                layout = 'Hybrid Bottom'
                hybrid_ratio = '3'
            case _ as screen_layout:
                layout = screen_layout

        core_options.set('melonds_screen_layout', layout)
        core_options.set('melonds_hybrid_ratio', hybrid_ratio)
