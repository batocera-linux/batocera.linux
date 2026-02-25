from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class MednafenSupergrafx(Core):
    supports_retroachievements: ClassVar = True

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Remove 16-sprites-per-scanline hardware limit
        core_options.set_from_config('sgx_nospritelimit', default='enabled')
