from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import RACore

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Vb(RACore):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # 2D Color Mode
        core_options.set_from_config('vb_color_mode', '2d_color_mode', default='black & red')

        # 3D Glasses Color Mode
        core_options.set_from_config('vb_anaglyph_preset', '3d_color_mode', default='disabled')
