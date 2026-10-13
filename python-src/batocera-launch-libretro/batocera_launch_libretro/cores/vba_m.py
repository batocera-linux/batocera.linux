from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import RACore

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class VbaM(RACore):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # GB / GBC / GBA: Auto select fine hardware mode
        # Emulator AUTO mode not working fine
        core_options.set('vbam_gbHardware', self.system)

        if self.system == 'gb':
            # GB: Colorisation of GB games
            palette = self.config.get('palettes', 'black and white')
            core_options.set('vbam_palettes', 'wierd colors' if palette == 'weird colors' else palette)

            # GB: Color Correction
            core_options.set_from_config('vbam_lcdfilter', 'gbcoloroption_gb', default='disabled')

        if self.system == 'gbc':
            # GBC: Color Correction
            core_options.set_from_config('vbam_lcdfilter', 'gbcoloroption_gbc', default='disabled')

        if self.system == 'gba':
            # GBA: Solar sensor level, Boktai 1: The Sun is in Your Hand
            core_options.set_from_config('vbam_solarsensor', 'solarsensor', default='0')

            # GBA: Sensor Sensitivity (Gyroscope) (%)
            core_options.set_from_config('vbam_gyro_sensitivity', 'gyro_sensitivity', default='10')

            # GBA: Sensor Sensitivity (Tilt) (%)
            core_options.set_from_config('vbam_tilt_sensitivity', 'tilt_sensitivity', default='10')
