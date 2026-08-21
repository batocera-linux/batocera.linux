from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class Quasi88(Core):
    supports_retroachievements: ClassVar = True

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # PC Model
        core_options.set_from_config('q88_basic_mode', default='N88 V2')

        # CPU clock (Overclock)
        core_options.set_from_config('q88_cpu_clock', default='4')

        # Use PCG-8100
        core_options.set_from_config('q88_pcg-8100', default='disabled')
