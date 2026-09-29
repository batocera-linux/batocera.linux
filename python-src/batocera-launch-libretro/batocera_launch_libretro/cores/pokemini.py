from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import RACore

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Pokemini(RACore):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # LCD Filter
        core_options.set_from_config('pokemini_lcdfilter', default='dotmatrix')

        # LCD Ghosting Effects
        core_options.set_from_config('pokemini_lcdmode', default='analog')
