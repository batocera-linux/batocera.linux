from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.paths import ROMS
from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, DisableRewindMixin, DisableRunaheadMixin

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class Vitaquake2(DisableRewindMixin, DisableRunaheadMixin, Core):
    @cached_property
    def _mission(self) -> tuple[str, Path]:
        # vitaquake2 - choose core based on directory
        name = self.rom.name.lower()

        if 'reckoning' in name:
            return 'vitaquake2-xatrix', ROMS / 'quake2' / 'xatrix' / 'pak0.pak'

        if 'zero' in name:
            return 'vitaquake2-rogue', ROMS / 'quake2' / 'rogue' / 'pak0.pak'

        if 'zaero' in name:
            return 'vitaquake2-zaero', ROMS / 'quake2' / 'zaero' / 'pak0.pak'

        return self.emulator.core, ROMS / 'quake2' / 'baseq2' / 'pak0.pak'

    @cached_property
    def library_prefix(self) -> str:
        return self._mission[0]

    @cached_property
    def rom_argument(self) -> str | Path | None:
        return self._mission[1]
