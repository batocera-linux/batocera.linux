from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, DisableRunaheadMixin, LibretroConfig


@cached_dataclass
class Ppsspp(DisableRunaheadMixin, Core):
    supports_retroachievements: ClassVar = True

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        core_options.set_from_config('ppsspp_internal_resolution', 'ppsspp_resolution', default='480x272')
