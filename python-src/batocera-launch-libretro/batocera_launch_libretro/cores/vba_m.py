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
