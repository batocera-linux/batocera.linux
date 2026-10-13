from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch_libretro import RACore

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Pce(RACore):
    @cached_property
    def player1_device_type(self) -> str | None:
        return self.config.get_str('controller1_pce', '1')

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Remove 16-sprites-per-scanline hardware limit
        prefix = 'pce_fast' if self.emulator.core == 'pce_fast' else 'pce'
        core_options.set_from_config(f'{prefix}_nospritelimit', 'pce_nospritelimit', default='enabled')
