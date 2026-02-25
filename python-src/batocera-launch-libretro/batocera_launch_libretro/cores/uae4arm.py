from __future__ import annotations

from batocera_common.paths import BIOS
from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, DisableRunaheadMixin, LibretroConfig


@cached_dataclass
class Uae4arm(DisableRunaheadMixin, Core):
    def set_config(self, custom_config: LibretroConfig, /) -> None:
        super().set_config(custom_config)

        # AMIGA BIOS files are in /userdata/bios/amiga
        custom_config.set('system_directory', f'{BIOS / "amiga"}/')
