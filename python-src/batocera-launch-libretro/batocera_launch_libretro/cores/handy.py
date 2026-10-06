from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import RACore

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Handy(RACore):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Display rotation
        # Set this option to start game at 'None' because it crash the emulator
        core_options.set('handy_rot', 'None')
