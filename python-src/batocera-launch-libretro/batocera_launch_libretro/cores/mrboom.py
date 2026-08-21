from __future__ import annotations

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class Mrboom(Core):
    @property
    def disables_bezel(self) -> bool:
        return True

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Team mode
        core_options.set_from_config('mrboom-aspect', 'mrboom-aspect', default='Native')
