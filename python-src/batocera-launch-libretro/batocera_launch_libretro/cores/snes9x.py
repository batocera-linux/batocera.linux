from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig, SquashFSMixin

from ._snes9x_core import Snes9xControllersMixin

if TYPE_CHECKING:
    from batocera_launch import Gun


@cached_dataclass
class Snes9x(SquashFSMixin, Snes9xControllersMixin, Core):
    supports_retroachievements: ClassVar = True
    squashfs_rom_globs: ClassVar = {
        'snes-msu1': ('*.sfc', '*.smc'),
        'satellaview': ('*.sfc', '*.smc'),
    }
    gun_mapping: ClassVar = {
        'default': {
            'device': 260,
            'p2': 0,
            'p3': 1,
            'gameDependant': [
                {'key': 'type', 'value': 'justifier', 'mapkey': 'device', 'mapvalue': '516'},
                {'key': 'type', 'value': 'justifier', 'mapkey': 'device_p3', 'mapvalue': '772'},
                {'key': 'type', 'value': 'macsrifle', 'mapkey': 'device', 'mapvalue': '1028'},
                {
                    'key': 'reversedbuttons',
                    'value': 'true',
                    'mapcorekey': 'snes9x_superscope_reverse_buttons',
                    'mapcorevalue': 'enabled',
                },
            ],
        }
    }

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Reduce sprite flickering (Hack, Unsafe)
        core_options.set_from_config('snes9x_reduce_sprite_flicker', 'reduce_sprite_flicker', default='enabled')

        # Reduce Slowdown (Hack, Unsafe)
        core_options.set_from_config('snes9x_overclock_cycles', 'reduce_slowdown', default='disabled')

        # SuperFX Overclocking
        core_options.set_from_config('snes9x_overclock_superfx', 'overclock_superfx', default='100%')

        # Hi-Res Blending
        core_options.set_from_config('snes9x_hires_blend', 'hires_blend', default='disabled')

        # Blargg NTSC Filter
        core_options.set_from_config('snes9x_blargg', 'snes9x_blargg_filter', default='disabled')

        # Crosshair
        crosshair = self.config.get('superscope_crosshair') or ('2' if self.emulator.guns_need_crosses else '0')
        core_options.set('snes9x_superscope_crosshair', crosshair)
        core_options.set('snes9x_justifier1_crosshair', crosshair)
        core_options.set('snes9x_justifier2_crosshair', crosshair)
        core_options.set('snes9x_rifle_crosshair', crosshair)

        if self.config.use_guns and self.guns:
            core_options.set('snes9x_superscope_reverse_buttons', 'disabled')

    def get_pedal_config_name_for_player(self, player_number: int, /) -> str:
        if self.metadata.get('gun_type') == 'justifier':
            return f'input_player{player_number}_gun_start'
        return f'input_player{player_number}_gun_aux_a'

    def set_gun_config_for_player(self, custom_config: LibretroConfig, player_number: int, gun: Gun, /) -> None:
        if self.metadata.get('gun_type') == 'justifier':
            custom_config.set(f'input_player{player_number}_gun_offscreen_shot_mbtn', '')
            custom_config.set(f'input_player{player_number}_gun_start_mbtn', 2)
        else:
            custom_config.set(f'input_player{player_number}_gun_offscreen_shot_mbtn', '')
            custom_config.set(f'input_player{player_number}_gun_start_mbtn', '')
            custom_config.set(f'input_player{player_number}_gun_select_mbtn', '')
            custom_config.set(f'input_player{player_number}_gun_aux_a_mbtn', 2)
            custom_config.set(f'input_player{player_number}_gun_aux_b_mbtn', 3)
            custom_config.set(f'input_player{player_number}_gun_start_mbtn', 4)
