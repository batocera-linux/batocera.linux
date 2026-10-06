from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass, cached_property

from .base import MAMEBase
from .command import MAMECommand
from .controllers import MAMEControllers

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_launch import Gun, LibretroConfig


@cached_dataclass
class MAME(MAMEControllers, MAMECommand, MAMEBase):
    @cached_property
    def rom_argument(self) -> str | Path | None:
        return self.cmd_filename

    def generate_special_configs(self) -> None:
        super().generate_special_configs()

        self.write_cmd_file()
        self.write_controllers_config()

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        if self.config.core != 'same_cdi':
            # Lightgun mode
            core_options.set('mame_lightgun_mode', 'lightgun')

            # Enable cheats
            core_options.set('mame_cheats_enable', 'enabled')

            # CPU Overclock
            core_options.set_from_config('mame_cpu_overclock', default='default')

            # Video Resolution
            core_options.set_from_config('mame_altres', default='640x480')

            # Disable controller profiling
            core_options.set('mame_buttons_profiles', 'disabled')

            # Software Lists (MESS)
            core_options.set('mame_softlists_enable', 'disabled')
            core_options.set('mame_softlists_auto_media', 'disabled')

            # Enable config reading (for controls)
            core_options.set('mame_read_config', 'enabled')

            # Use CLI (via CMD file) to boot
            core_options.set('mame_boot_from_cli', 'enabled')

            # Activate mouse for Mac & Archimedes
            core_options.set(
                'mame_mouse_enable', 'enabled' if self.system in {'macintosh', 'archimedes'} else 'disabled'
            )

        else:
            # Lightgun mode
            core_options.set('same_cdi_lightgun_mode', 'lightgun')

            # Enable cheats
            core_options.set('same_cdi_cheats_enable', 'enabled')

            # CPU Overclock
            core_options.set_from_config('same_cdi_cpu_overclock', default='default')

            # Video Resolution
            core_options.set_from_config('same_cdi_altres', default='640x480')

            # Disable controller profiling
            core_options.set('same_cdi_buttons_profiles', 'disabled')
            # Software Lists (MESS)
            core_options.set('same_cdi_softlists_enable', 'disabled')
            core_options.set('same_cdi_softlists_auto_media', 'disabled')
            # Enable config reading (for controls)
            core_options.set('same_cdi_read_config', 'enabled')
            # Use CLI (via CMD file) to boot
            core_options.set('same_cdi_boot_from_cli', 'enabled')
            # Activate mouse
            core_options.set('same_cdi_mouse_enable', 'enabled')

    def get_pedal_config_name_for_player(self, player_number: int, /) -> str:
        return f'input_player{player_number}_gun_aux_a'

    def set_gun_config_for_player(self, custom_config: LibretroConfig, player_number: int, gun: Gun, /) -> None:
        custom_config.set(f'input_player{player_number}_gun_offscreen_shot_mbtn', '')
        custom_config.set(f'input_player{player_number}_gun_aux_a_mbtn', 2)
        custom_config.set(f'input_player{player_number}_start_mbtn', 3)
        custom_config.set(f'input_player{player_number}_select_mbtn', 4)
