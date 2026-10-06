from __future__ import annotations

from batocera_common.dataclasses import cached_dataclass, cached_property

from .config.decoration_id import get_decoration_id
from .emulator import Emulator


@cached_dataclass
class SpecialDecorationsMixin(Emulator):
    @cached_property
    def decoration_id(self) -> str:
        return get_decoration_id(self.system, self.rom.stem)
