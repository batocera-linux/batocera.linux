# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch_libretro import Core

if TYPE_CHECKING:
    from batocera_launch import Gun, LibretroConfig


@cached_dataclass
class MAME078Plus(Core):
    gun_mapping: ClassVar = {'default': {'device': 4, 'p1': 0, 'p2': 1}}

    def precalibrate_guns(self) -> None:
        if self.system != 'mame':
            return

        # mame2003-plus reads its own nvram files
        src = self.emulator.gun_precalibration_dir / 'mame2003-plus' / 'nvram' / f'{self.rom.stem}.nv'
        dest = self.emulator.saves_dir / 'mame2003-plus' / 'nvram' / f'{self.rom.stem}.nv'

        if src.is_file() and not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            src.copy(dest)

    @cached_property
    def map_lightguns(self) -> bool:
        return self.config.get_bool('lightgun_map')

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Skip Disclaimer and Warnings
        core_options.set('mame2003-plus_skip_disclaimer', 'enabled')
        core_options.set('mame2003-plus_skip_warnings', 'enabled')

        # Frameskip
        core_options.set_from_config('mame2003-plus_frameskip', default='disabled')

        # Vector resolution
        core_options.set_from_config('mame2003-plus_vector_resolution', default='1024x768')

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
