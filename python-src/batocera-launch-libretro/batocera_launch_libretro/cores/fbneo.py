from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from batocera_launch_libretro import Core, LibretroConfig

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_launch import Gun


@dataclass(slots=True)
class Fbneo(Core):
    supports_retroachievements: ClassVar = True
    gun_mapping: ClassVar = {'default': {'device': 4, 'p1': 0, 'p2': 1}}

    def get_command_arguments(self) -> list[str | Path] | None:
        if self.system == 'neogeocd':
            return ['--subsystem', 'neocd']

        return None

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Diagnostic input
        core_options.set('fbneo-diagnostic-input', 'Start + L + R')

        # Allow RetroAchievements in hardcore mode with FBNeo
        core_options.set('fbneo-allow-patched-romsets', 'disabled')

        # CPU Clock
        core_options.set_from_config('fbneo-cpu-speed-adjust', 'fbneo-cpu-speed-adjust', default='100%')

        # Frameskip
        core_options.set_from_config('fbneo-frameskip', 'fbneo-frameskip', default='0')

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
                elif mode_switch == 'AES Asia':
                    core_options.set(f'fbneo-dipswitch-{self.rom.id}-BIOS', 'AES Asia')
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
