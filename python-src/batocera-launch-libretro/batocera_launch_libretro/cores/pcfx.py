from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import RACore

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Pcfx(RACore):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Remove 16-sprites-per-scanline hardware limit
        core_options.set_from_config('pcfx_nospritelimit', default='enabled')
