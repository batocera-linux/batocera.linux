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
from batocera_launch_libretro import GLCoreOverrideMixin, RACore

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Kronos(GLCoreOverrideMixin, RACore):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Video Resolution
        core_options.set_from_config('kronos_resolution_mode', 'kronos_resolution', default='original')

        # Mesh mode
        core_options.set_from_config('kronos_meshmode', default='disabled')

        # Banding mode
        core_options.set_from_config('kronos_bandingmode', default='disabled')

        # Share saves with Beetle
        core_options.set_from_config('kronos_use_beetle_saves', default='enabled')

        # Multitap
        port1 = 'disabled'
        port2 = 'disabled'

        match self.config.get('kronos_multitap'):
            case 'port1':
                port1 = 'enabled'
            case 'port2':
                port2 = 'enabled'
            case 'port12':
                port1 = 'enabled'
                port2 = 'enabled'
            case _:
                pass

        core_options.set('kronos_multitap_port1', port1)
        core_options.set('kronos_multitap_port2', port2)

        # BIOS langauge
        core_options.set_from_config('kronos_language_id', default='English')
