from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, SquashFSMixin


@cached_dataclass
class Pocketsnes(SquashFSMixin, Core):
    squashfs_rom_globs: ClassVar = {
        'snes-msu1': ('*.sfc', '*.smc'),
        'satellaview': ('*.sfc', '*.smc'),
    }
