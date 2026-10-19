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
class Fuse(Core):
    @cached_property
    def player1_device_type(self) -> str | None:
        return self.config.get_str('controller1_zxspec', '769')  # 769 = Sinclair 1 controller - most used on games

    @cached_property
    def player2_device_type(self) -> str | None:
        return self.config.get_str('controller2_zxspec', '1025')  # 1025 = Sinclair 2 controller

    @cached_property
    def player3_device_type(self) -> str | None:
        return self.config.get_str('controller3_zxspec', '259')

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # The most common configuration same as ZX Spectrum+
        core_options.set_from_config('fuse_machine', 'fuse_machine', default='Spectrum 128K')

        # Video border size
        default = 'none' if self.config.get('fuse_hide_border') == 'enabled' else 'full'
        core_options.set_from_config('fuse_size_border', 'fuse_size_border', default=default)
