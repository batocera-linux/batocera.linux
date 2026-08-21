from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class Pce(Core):
    supports_retroachievements: ClassVar = True

    @cached_property
    def player1_device_type(self) -> str | None:
        return self.config.get_str('controller1_pce', '1')

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Remove 16-sprites-per-scanline hardware limit
        core_options.set_from_config('pce_nospritelimit', default='enabled')
