from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import GLOverrideMixin, RACore

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Ppsspp(GLOverrideMixin, RACore):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        core_options.set_from_config('ppsspp_internal_resolution', 'ppsspp_resolution', default='480x272')
