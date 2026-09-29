from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import RACore

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Potator(RACore):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Watara Color Palette
        core_options.set_from_config('potator_palette', 'watara_palette', default='gameking')

        # Watara Ghosting
        core_options.set_from_config('potator_lcd_ghosting', 'watara_ghosting', default='0')
