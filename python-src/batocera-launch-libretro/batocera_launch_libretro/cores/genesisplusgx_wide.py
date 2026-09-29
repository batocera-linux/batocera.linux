from __future__ import annotations

from typing import ClassVar

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import RACore, SquashFSMixin


@cached_dataclass
class GenesisPlusGXWide(SquashFSMixin, RACore):
    squashfs_rom_globs: ClassVar = {'megadrive-msu': ('*.md',)}
