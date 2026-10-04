from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass
from batocera_common.paths import BIOS
from batocera_launch_libretro import Core

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Uae4arm(Core):
    def set_config(self, custom_config: LibretroConfig, /) -> None:
        super().set_config(custom_config)

        # AMIGA BIOS files are in /userdata/bios/amiga
        custom_config.set('system_directory', f'{BIOS / "amiga"}/')
