from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, DisableRewindMixin, DisableRunaheadMixin, GLOverrideMixin

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class Boom3(GLOverrideMixin, DisableRewindMixin, DisableRunaheadMixin, Core):
    @cached_property
    def _resolved_rom(self) -> Path:
        with self.rom.open() as file:
            first_line = file.readline().strip()

        return self.rom.parent / first_line

    @cached_property
    def library_prefix(self) -> str:
        return 'boom3_xp' if 'd3xp' in self._resolved_rom.parent.parts else self.emulator.core

    @cached_property
    def rom_argument(self) -> str | Path | None:
        return self._resolved_rom
