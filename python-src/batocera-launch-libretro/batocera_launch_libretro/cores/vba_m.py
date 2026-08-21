from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class VbaM(Core):
    supports_retroachievements: ClassVar = True

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # GB / GBC / GBA: Auto select fine hardware mode
        # Emulator AUTO mode not working fine
        core_options.set('vbam_gbHardware', self.system)

        if self.system == 'gb':
            # GB: Colorisation of GB games
            core_options.set_from_config('vbam_palettes', 'palettes', default='black and white')

            # GB: Color Correction
            core_options.set_from_config('vbam_gbcoloroption', 'gbcoloroption_gb', default='disabled')

        if self.system == 'gbc':
            # GBC: Color Correction
            core_options.set_from_config('vbam_gbcoloroption', 'gbcoloroption_gbc', default='disabled')

        if self.system == 'gba':
            # GBA: Solar sensor level, Boktai 1: The Sun is in Your Hand
            core_options.set_from_config('vbam_solarsensor', 'solarsensor', default='0')

            # GBA: Sensor Sensitivity (Gyroscope) (%)
            core_options.set_from_config('vbam_gyro_sensitivity', 'gyro_sensitivity', default='10')

            # GBA: Sensor Sensitivity (Tilt) (%)
            core_options.set_from_config('vbam_tilt_sensitivity', 'tilt_sensitivity', default='10')
