from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class Nestopia(Core):
    gun_mapping: ClassVar = {'default': {'device': 262, 'p2': 0}}

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # gun
        core_options.set(
            'nestopia_zapper_device', 'lightgun' if self.config.use_guns and self.guns else 'mouse'
        )  # Mouse mode for Zapper

        # gun cross
        core_options.set_from_config(
            'nestopia_show_crosshair',
            default='enabled' if self.emulator.guns_need_crosses else 'disabled',
        )

        # Reduce Sprite Flickering
        core_options.set_from_config('nestopia_nospritelimit', default='enabled')

        # Crop Overscan
        match self.config.get('nestopia_cropoverscan'):
            case 'none':
                overscan_h = '0'
                overscan_v = '0'
            case 'h':
                overscan_h = '8'
                overscan_v = '0'
            case 'both':
                overscan_h = '8'
                overscan_v = '8'
            case _:
                overscan_h = '0'
                overscan_v = '8'
        core_options.set('nestopia_overscan_h_left', overscan_h)
        core_options.set('nestopia_overscan_h_right', overscan_h)
        core_options.set('nestopia_overscan_v_top', overscan_v)
        core_options.set('nestopia_overscan_v_bottom', overscan_v)

        # Palette Choice
        core_options.set_from_config('nestopia_palette', default='consumer')

        # NTSC Filter
        core_options.set_from_config('nestopia_blargg_ntsc_filter', default='disabled')

        # CPU Overclock
        core_options.set_from_config('nestopia_overclock', default='1x')

        # 4 Player Adapter
        adapter = self.config.get('nestopia_select_adapter', 'automatic')
        core_options.set('nestopia_select_adapter', 'auto' if adapter == 'automatic' else adapter)
