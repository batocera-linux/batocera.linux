from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch_libretro import Core

if TYPE_CHECKING:
    from batocera_launch import Gun, LibretroConfig


@cached_dataclass
class MAME078Plus(Core):
    gun_mapping: ClassVar = {'default': {'device': 4, 'p1': 0, 'p2': 1}}

    @cached_property
    def map_lightguns(self) -> bool:
        return self.config.get_bool('lightgun_map')

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Skip Disclaimer and Warnings
        core_options.set('mame2003-plus_skip_disclaimer', 'enabled')
        core_options.set('mame2003-plus_skip_warnings', 'enabled')

        # Control Mapping
        core_options.set_from_config('mame2003-plus_analog', default='digital')

        # Frameskip
        core_options.set_from_config('mame2003-plus_frameskip', default='0')

        # Input interface
        core_options.set_from_config('mame2003-plus_input_interface', default='retropad')

        # TATE Mode
        core_options.set_from_config('mame2003-plus_tate_mode', default='disabled')

        # NEOGEO Bios
        core_options.set_from_config('mame2003-plus_neogeo_bios', default='unibios33')

        # gun
        core_options.set('mame2003-plus_xy_device', 'lightgun' if self.config.use_guns and self.guns else 'mouse')

        # gun cross
        core_options.set_from_config(
            'mame2003-plus_crosshair_enabled',
            default='enabled' if self.emulator.guns_need_crosses else 'disabled',
        )

    def set_gun_config_for_player(self, custom_config: LibretroConfig, player_number: int, gun: Gun, /) -> None:
        custom_config.set(f'input_player{player_number}_gun_offscreen_shot_mbtn', '')
        custom_config.set(f'input_player{player_number}_gun_start_mbtn', '')
        custom_config.set(f'input_player{player_number}_gun_select_mbtn', '')
        custom_config.set(f'input_player{player_number}_gun_aux_a_mbtn', '')
        custom_config.set(f'input_player{player_number}_gun_aux_b_mbtn', '')
        custom_config.set(f'input_player{player_number}_gun_start_mbtn', 3)
        custom_config.set(f'input_player{player_number}_gun_select_mbtn', 4)
