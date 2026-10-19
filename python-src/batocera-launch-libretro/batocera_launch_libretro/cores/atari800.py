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

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch_libretro import Core

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Atari800(Core):
    @cached_property
    def player1_device_type(self) -> str | None:
        return '513'

    @cached_property
    def player2_device_type(self) -> str | None:
        return '513'

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        if self.system == 'atari800':
            # Select Atari 800
            # Let user overide Atari System
            core_options.set_from_config('atari800_system', default='800XL (64K)')

            # Video Standard
            core_options.set_from_config('atari800_ntscpal', default='NTSC')

            # SIO Acceleration
            core_options.set_from_config('atari800_sioaccel', default='enabled')

            # Hi-Res Artifacting
            legacy = 'blue/brown 1' if self.config.get('atari800_artifacting') == 'enabled' else 'none'
            core_options.set_from_config('atari800_artifacting_mode', default=legacy)

            # Internal resolution
            core_options.set_from_config('atari800_resolution')  # Default : 336x240

            # Internal BASIC interpreter
            core_options.set_from_config('atari800_internalbasic', default='disabled')

            # WARNING: Now we must stop to use "atari800.cfg" because core options crush them

        else:
            # Select Atari 5200
            core_options.set('atari800_system', '5200')

            # Joy Hack (for robotron)
            core_options.set_from_config('atari800_opt2', default='disabled')
