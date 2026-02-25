from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, DisableRewindMixin, DisableRunaheadMixin, LibretroConfig


@cached_dataclass
class Neocd(DisableRewindMixin, DisableRunaheadMixin, Core):
    supports_retroachievements: ClassVar = True

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Console region
        core_options.set_from_config('neocd_region', 'neocd_region', default='Japan')

        # BIOS Select
        core_options.set_from_config('neocd_bios', 'neocd_bios', default='neocd_z.rom (CDZ)')

        # Per-Game saves
        core_options.set_bool_from_config('neocd_per_content_saves', default=True, values=('On', 'Off'))
