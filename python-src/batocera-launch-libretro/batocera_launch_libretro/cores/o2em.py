from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class O2em(Core):
    supports_retroachievements: ClassVar = True

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Virtual keyboard transparency
        core_options.set('o2em_vkbd_transparency', '25')

        # Emulated Hardware
        core_options.set_from_config('o2em_bios', default='g7400.bin' if self.system == 'videopacplus' else 'o2rom.bin')

        # Emulated Hardware
        region = self.config.get('o2em_region', 'autodetect')
        core_options.set('o2em_region', 'auto' if region == 'autodetect' else region)

        # Swap Gamepad
        core_options.set_from_config('o2em_swap_gamepads', default='disabled')

        # Crop Overscan
        core_options.set_from_config('o2em_crop_overscan', default='enabled')

        # Ghosting effect
        core_options.set_from_config('o2em_mix_frames', default='disabled')

        # Audio Filter
        low_pass_range = self.config.get('o2em_low_pass_range', '0')
        core_options.set('o2em_low_pass_filter', 'disabled' if low_pass_range == '0' else 'enabled')
        core_options.set('o2em_low_pass_range', low_pass_range)
