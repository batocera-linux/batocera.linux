from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class Pokemini(Core):
    supports_retroachievements: ClassVar = True

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # LCD Filter
        core_options.set_from_config('pokemini_lcdfilter', default='dotmatrix')

        # LCD Ghosting Effects
        core_options.set_from_config('pokemini_lcdmode', default='analog')
