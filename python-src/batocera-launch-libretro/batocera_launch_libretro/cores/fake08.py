from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, DisableRunaheadMixin

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class Fake08(DisableRunaheadMixin, Core):
    @cached_property
    def rom_argument(self) -> str | Path | None:
        rom = self.rom

        # Pico-8 multi-carts (might work only with official Lexaloffe engine right now)
        if rom.suffix.lower() == '.m3u':
            with rom.open() as fpin:
                lines = fpin.readlines()

            return rom.absolute().parent / lines[0].strip()

        return rom
