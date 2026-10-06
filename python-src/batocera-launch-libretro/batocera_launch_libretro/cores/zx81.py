from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch_libretro import Core

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class ZX81(Core):
    @cached_property
    def player1_device_type(self) -> str | None:
        return '259'

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Tape Fast Load
        core_options.set('81_fast_load', 'enabled')
        # Enables sound emulatio
        core_options.set('81_sound', 'Zon X-81')
        # Colorisation (Chroma 81)
        if chroma := self.config.get('81_chroma_81'):
            if chroma == 'automatic':
                core_options.set('81_chroma_81', 'auto')
            else:
                core_options.set('81_chroma_81', chroma)
        else:
            core_options.set('81_chroma_81', 'enabled')
        # High Resolution
        if hires := self.config.get('81_highres'):
            if hires == 'automatic':
                core_options.set('81_highres', 'auto')
            else:
                core_options.set('81_highres', hires)
        else:
            core_options.set('81_highres', 'WRX')
