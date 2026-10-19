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

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch_libretro import RACore

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class BeetleSaturn(RACore):
    gun_mapping: ClassVar = {'default': {'device': 260, 'p1': 0, 'p2': 1}}

    @cached_property
    def player1_device_type(self) -> str | None:
        if self.system != 'saturn':
            return None

        # wheel
        if self.config.use_wheels:
            return '517'  # Arcade Racer

        return self._saturn_device_type('controller1_saturn')

    @cached_property
    def player2_device_type(self) -> str | None:
        if self.system != 'saturn':
            return None

        return self._saturn_device_type('controller2_saturn')

    def _saturn_device_type(self, key: str, /) -> str:
        # shared with yabasanshiro, which used to store its 3D Pad as 5
        device = self.config.get_str(key, '1')  # 1 = Saturn pad
        return '261' if device == '5' else device

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # gun cross / wheel
        # gun
        core_options.set_from_config(
            'beetle_saturn_virtuagun_crosshair',
            'beetle-saturn_crosshair',
            default='Cross' if self.emulator.guns_need_crosses else 'Off',
        )

        # wheel
        core_options.set(
            'beetle_saturn_analog_stick_deadzone', '0%' if self.config.use_wheels and self.wheels else '15%'
        )
