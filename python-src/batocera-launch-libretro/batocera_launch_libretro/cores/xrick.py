from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import Core

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Xrick(Core):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Crop Borders
        core_options.set_bool_from_config('xrick_crop_borders', default=True, values=('enabled', 'disabled'))

        # Cheat 1 (Trainer Mode)
        core_options.set_bool_from_config('xrick_cheat1', values=('enabled', 'disabled'))

        # Cheat 2 (Invulnerablilty Mode)
        core_options.set_bool_from_config('xrick_cheat2', values=('enabled', 'disabled'))

        # Cheat 3 (Expose Mode)
        core_options.set_bool_from_config('xrick_cheat3', values=('enabled', 'disabled'))
