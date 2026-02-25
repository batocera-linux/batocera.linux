from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class VirtualJaguar(Core):
    supports_retroachievements: ClassVar = True

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Fast Blitter (Older, Faster, Less compatible)
        core_options.set_from_config('virtualjaguar_usefastblitter', 'usefastblitter', default='enabled')

        # Show Bios Bootlogo
        core_options.set_from_config('virtualjaguar_bios', 'bios_vj', default='enabled')

        # Doom Res Hack
        core_options.set_from_config('virtualjaguar_doom_res_hack', 'doom_res_hack', default='disabled')
