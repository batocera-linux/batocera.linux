from __future__ import annotations

from typing import TYPE_CHECKING, Final

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import RACore

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig

# The core reads attack on Y, jump on B and special on A; keep the standalone OpenBOR layout
_ANYBOR_REMAP_VALUES: Final = {
    'btn_b': '1',
    'btn_a': '0',
    'btn_y': '8',
}


@cached_dataclass
class AnyBOR(RACore):
    def set_config(self, custom_config: LibretroConfig, /) -> None:
        for pad in self.controllers[:4]:
            for btn, value in _ANYBOR_REMAP_VALUES.items():
                custom_config.set(f'input_player{pad.player_number}_{btn}', value)
