from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class Mesen(Core):
    supports_retroachievements: ClassVar = True
    gun_mapping: ClassVar = {'default': {'device': 262, 'p1': 0}}

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        core_options.set_from_config('mesen_region', default='Auto')

        # Screen rotation (for homebrew)
        core_options.set_from_config('mesen_screenrotation', default='None')

        # NTSC Filter
        core_options.set_from_config('mesen_ntsc_filter', default='Disabled')

        # Sprite limit removal
        core_options.set_from_config('mesen_nospritelimit', default='disabled')

        # Palette
        core_options.set_from_config('mesen_palette', default='Default')

        # HD texture replacements
        core_options.set_from_config('mesen_hdpacks', default='enabled')

        # FDS Auto-insert side A
        core_options.set_from_config('mesen_fdsautoinsertdisk', default='disabled')

        # FDS Fast forward floppy disk loading
        core_options.set_from_config('mesen_fdsfastforwardload', default='disabled')

        # RAM init state (speedrunning)
        core_options.set_from_config('mesen_ramstate', default='All 0s (Default)')

        # NES CPU Overclock
        core_options.set_from_config('mesen_overclock', default='None')

        # Overclocking type (compatibility)
        core_options.set_from_config('mesen_overclock_type', default='Before NMI (Recommended)')
