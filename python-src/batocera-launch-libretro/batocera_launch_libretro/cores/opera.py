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
    from batocera_launch import LibretroConfig


@cached_dataclass
class Opera(RACore):
    gun_mapping: ClassVar = {'default': {'device': 260, 'p1': 0, 'p2': 1}}

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Audio Process on separate CPU thread
        core_options.set('opera_dsp_threaded', 'enabled')

        # High Resolution (640x480)
        core_options.set_from_config('opera_high_resolution', 'high_resolution', default='enabled')

        # CPU Overclock
        core_options.set_from_config('opera_cpu_overclock', 'cpu_overclock', default='1.0x (12.50Mhz)')

        # Active Input Devices Fix
        core_options.set_from_config('opera_active_devices', 'active_devices', default='1')

        # Shared nvram
        # If ROM includes the word Disc, assume it's a multi disc game, and enable shared nvram if the option isn't set.
        storage = self.config.get('opera_nvram_storage')

        if not storage:
            storage = 'shared' if 'disc' in str(self.rom).casefold() else 'per game'

        core_options.set('opera_nvram_storage', storage)
