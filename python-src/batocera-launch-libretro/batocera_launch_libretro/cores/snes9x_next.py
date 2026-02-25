from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig

from ._snes9x_core import Snes9xControllersMixin


@cached_dataclass
class Snes9xNext(Snes9xControllersMixin, Core):
    supports_retroachievements: ClassVar = True
    gun_mapping: ClassVar = {
        'default': {
            'device': 260,
            'p2': 0,
            'gameDependant': [{'key': 'type', 'value': 'justifier', 'mapkey': 'device', 'mapvalue': '516'}],
        }
    }

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Reduce sprite flickering (Hack, Unsafe)
        core_options.set_from_config(
            'snes9x_2010_reduce_sprite_flicker', '2010_reduce_sprite_flicker', default='enabled'
        )

        # Reduce Slowdown (Hack, Unsafe)
        core_options.set_from_config('snes9x_2010_overclock_cycles', '2010_reduce_slowdown', default='disabled')

        # SuperFX Overclocking
        core_options.set_from_config('snes9x_2010_overclock', '2010_overclock_superfx', default='10 MHz (Default)')

        # Blargg NTSC Filter
        core_options.set_from_config('snes9x_2010_blargg', 'snes9x_2010_blargg_filter', default='disabled')

        # Crosshair
        core_options.set_from_config(
            'snes9x_2010_superscope_crosshair',
            'superscope_crosshair',
            default='2' if self.emulator.guns_need_crosses else 'disabled',
        )
