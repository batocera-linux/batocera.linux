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

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import RACore

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_launch import Gun, LibretroConfig


@cached_dataclass
class Fbneo(RACore):
    gun_mapping: ClassVar = {'default': {'device': 4, 'p1': 0, 'p2': 1}}

    def get_command_arguments(self) -> list[str | Path] | None:
        if self.system == 'neogeocd':
            return ['--subsystem', 'neocd']

        return None

    def set_config(self, custom_config: LibretroConfig, /) -> None:
        super().set_config(custom_config)

        custom_config.set('input_player1_select', 'f12')

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Diagnostic input
        core_options.set('fbneo-diagnostic-input', 'Start + L + R')

        # Allow RetroAchievements in hardcore mode with FBNeo
        core_options.set('fbneo-allow-patched-romsets', 'disabled')

        # CPU Clock
        core_options.set_from_config('fbneo-cpu-speed-adjust', 'fbneo-cpu-speed-adjust', default='100%')

        # Frameskip
        frameskip = self.config.get('fbneo-frameskip', '0')
        core_options.set('fbneo-frameskip-type', 'Fixed' if frameskip != '0' else 'disabled')
        core_options.set('fbneo-fixed-frameskip', frameskip)

        # Crosshair (Lightgun)
        core_options.set_from_config(
            'fbneo-lightgun-crosshair-emulation',
            default='always show' if self.emulator.guns_need_crosses else 'always hide',
        )
        core_options.set(
            f'fbneo-dipswitch-{self.rom.id}-Controls', 'Light Gun' if self.config.use_guns and self.guns else 'Joystick'
        )

        # NEOGEO
        if self.system == 'neogeo':
            # Neogeo Mode
            if mode_switch := self.config.get('fbneo-neogeo-mode-switch'):
                core_options.set('fbneo-neogeo-mode', 'DIPSWITCH')
                if mode_switch == 'MVS Asia/Europe':
                    core_options.set(f'fbneo-dipswitch-{self.rom.id}-BIOS', 'MVS Asia/Europe ver. 5 (1 slot)')
                elif mode_switch == 'MVS USA':
                    core_options.set(f'fbneo-dipswitch-{self.rom.id}-BIOS', 'MVS USA ver. 5 (2 slot)')
                elif mode_switch == 'MVS Japan':
                    core_options.set(f'fbneo-dipswitch-{self.rom.id}-BIOS', 'MVS Japan ver. 5 (? slot)')
                elif mode_switch in ('AES World', 'AES Asia'):
                    core_options.set(f'fbneo-dipswitch-{self.rom.id}-BIOS', 'AES World')
                elif mode_switch == 'AES Japan':
                    core_options.set(f'fbneo-dipswitch-{self.rom.id}-BIOS', 'AES Japan')
                else:
                    core_options.set('fbneo-neogeo-mode', 'UNIBIOS')
            else:
                core_options.set('fbneo-neogeo-mode', 'UNIBIOS')
                # core_options.set(f"fbneo-dipswitch-{rom.stem}-BIOS",      'Universe BIOS ver. 4.0')
            # Memory card mode
            core_options.set_from_config('fbneo-memcard-mode', 'fbneo-memcard-mode', default='per-game')

    def get_pedal_config_name_for_player(self, player_number: int, /) -> str:
        return f'input_player{player_number}_gun_aux_a'

    def set_gun_config_for_player(self, custom_config: LibretroConfig, player_number: int, gun: Gun, /) -> None:
        custom_config.set(f'input_player{player_number}_gun_offscreen_shot_mbtn', '')
        custom_config.set(f'input_player{player_number}_gun_aux_a_mbtn', 2)
