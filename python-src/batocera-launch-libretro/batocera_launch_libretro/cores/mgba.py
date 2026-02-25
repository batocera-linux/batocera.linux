from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class Mgba(Core):
    supports_retroachievements: ClassVar = True

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Skip BIOS intro
        core_options.set_bool_from_config('mgba_skip_bios', 'skip_bios_mgba', values=('ON', 'OFF'))

        # Rumble
        # This works because only '1' is treated as True in get_bool()
        core_options.set_bool_from_config('mgba_force_gbp', 'rumble_gain', default=True, values=('OFF', 'ON'))

        if self.system != 'gba':
            # GB / GBC: Color Correction
            color_correction = self.config.get('color_correction', 'False')
            core_options.set('mgba_color_correction', 'OFF' if color_correction == 'False' else color_correction)

        if self.system == 'gba':
            # GBA: Solar sensor level, Boktai 1: The Sun is in Your Hand
            core_options.set_from_config('mgba_solar_sensor_level', 'solar_sensor_level', default='0')

            # GBA: Frameskip
            core_options.set_from_config('mgba_frameskip', 'frameskip_mgba', default='0')

        # Force Super Game Boy mode for SGB system, auto for all others
        # No current option to override - add if needed.
        if self.system == 'sgb':
            core_options.set('mgba_gb_model', 'Super Game Boy')

            # Default border to on for SGB
            core_options.set_bool_from_config('mgba_sgb_borders', 'sgb_borders', default=True, values=('ON', 'OFF'))
        else:
            core_options.set('mgba_gb_model', 'Autodetect')
