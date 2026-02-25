from __future__ import annotations

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, DisableRunaheadMixin, LibretroConfig


@cached_dataclass
class Theodore(DisableRunaheadMixin, Core):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Auto run games
        core_options.set('theodore_autorun', 'enabled')
