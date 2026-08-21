from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, SquashFSMixin


@cached_dataclass
class GenesisPlusGXWide(SquashFSMixin, Core):
    supports_retroachievements: ClassVar = True
    squashfs_rom_globs: ClassVar = {'megadrive-msu': ('*.md',)}
