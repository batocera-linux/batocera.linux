from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import RACore, SquashFSMixin

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Bsnes(SquashFSMixin, RACore):
    squashfs_rom_globs: ClassVar = {
        'snes-msu1': ('*.sfc', '*.smc'),
        'sgb-msu1': ('*.gb', '*.gbc'),
    }
    gun_mapping: ClassVar = {
        'default': {
            'device': 260,
            'p2': 0,
            'gameDependant': [
                {'key': 'type', 'value': 'justifier', 'mapkey': 'device', 'mapvalue': '516'},
                {
                    'key': 'reversedbuttons',
                    'value': 'true',
                    'mapcorekey': 'bsnes_touchscreen_lightgun_superscope_reverse',
                    'mapcorevalue': 'ON',
                },
            ],
        }
    }

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        if self.config.use_guns and self.guns:
            core_options.set('bsnes_touchscreen_lightgun_superscope_reverse', 'OFF')

        # Video Filters
        core_options.set_from_config('bsnes_video_filter', default='disabled')

        # HD Mode 7 (bsnes_hd only, SNES systems)
        if self.config.core == 'bsnes_hd' and self.system in ('snes', 'snes-msu1'):
            core_options.set_from_config('bsnes_mode7_scale', default='disable')
            core_options.set_from_config('bsnes_mode7_supersample', default='none')
            core_options.set_from_config('bsnes_mode7_wsMode', default='Off')

        # SGB options
        if self.system == 'sgb-msu1':
            # BIOS
            core_options.set_from_config('bsnes_sgb_bios', default='SGB1.sfc')
            # Hide SGB border (bsnes only, not supported by bsnes_hd)
            if self.config.core == 'bsnes':
                core_options.set_from_config('bsnes_hide_sgb_border', default='OFF')
