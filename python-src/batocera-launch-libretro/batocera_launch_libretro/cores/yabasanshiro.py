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
from batocera_launch_libretro import Core, GLOverrideMixin

if TYPE_CHECKING:
    from batocera_launch import Controller, LibretroConfig


@cached_dataclass
class YabaSanshiro(GLOverrideMixin, Core):
    @cached_property
    def player1_device_type(self) -> str | None:
        if self.system != 'saturn':
            return None

        return self._saturn_device_type('controller1_saturn')

    @cached_property
    def player2_device_type(self) -> str | None:
        if self.system != 'saturn':
            return None

        return self._saturn_device_type('controller2_saturn')

    def _saturn_device_type(self, key: str, /) -> str:
        # shared with beetle-saturn, whose 3D Pad is 261
        device = self.config.get_str(key, '1')
        return '5' if device == '261' else device

    def set_button_mappings(self, controller: Controller, button_mappings: dict[str, str], /) -> None:
        # Fix for reversed inputs in Yabasanshiro core which is unmaintained by retroarch
        button_mappings['pageup'] = 'r'
        button_mappings['pagedown'] = 'l'

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Video Resolution
        core_options.set_from_config('yabasanshiro_resolution_mode', 'resolution_mode', default='original')

        # Rotating background resolution
        core_options.set_from_config(
            'yabasanshiro_rbg_resolution_mode', 'yabasanshiro_rbg_resolution', default='original'
        )

        # Multitap
        port1 = 'disabled'
        port2 = 'disabled'

        match self.config.get('multitap_yabasanshiro'):
            case 'port1':
                port1 = 'enabled'
            case 'port2':
                port2 = 'enabled'
            case 'port12':
                port1 = 'enabled'
                port2 = 'enabled'
            case _:
                pass

        core_options.set('yabasanshiro_multitap_port1', port1)
        core_options.set('yabasanshiro_multitap_port2', port2)

        # Language
        core_options.set_from_config('yabasanshiro_system_language', 'yabasanshiro_language', default='english')
