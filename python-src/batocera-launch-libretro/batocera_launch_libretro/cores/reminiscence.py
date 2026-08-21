from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, DisableRunaheadMixin

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class Reminiscence(DisableRunaheadMixin, Core):
    @cached_property
    def rom_argument(self) -> str | Path | None:
        with self.rom.open() as file:
            first_line = file.readline().strip()

        return self.rom.parent / first_line
