from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class Vb(Core):
    supports_retroachievements: ClassVar = True

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # 2D Color Mode
        core_options.set_from_config('vb_color_mode', '2d_color_mode', default='black & red')

        # 3D Glasses Color Mode
        core_options.set_from_config('vb_anaglyph_preset', '3d_color_mode', default='disabled')
