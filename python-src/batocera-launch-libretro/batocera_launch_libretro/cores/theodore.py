from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import Core

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Theodore(Core):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Auto run games
        core_options.set('theodore_autorun', 'enabled')
