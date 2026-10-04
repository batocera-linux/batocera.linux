from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import Core

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class GP32Emu(Core):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Boot the card straight into the game, the firmware menu waits for the player to pick it
        core_options.set_from_config('gp32emu_boot_mode', default='direct_hle')
