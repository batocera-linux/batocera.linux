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

from batocera_common.dataclasses import cached_dataclass, cached_property

from ..core import Core


@cached_dataclass
class Snes9xControllersMixin(Core):
    @cached_property
    def player1_device_type(self) -> str | None:
        if (controller := self.config.get_str('controller1_snes9x')) is not None:
            return controller
        if (controller := self.config.get_str('controller1_snes9x_next')) is not None:
            return controller
        return '1'

    @cached_property
    def player2_device_type(self) -> str | None:
        if (controller := self.config.get_str('controller2_snes9x')) is not None:
            return controller
        if (controller := self.config.get_str('controller2_snes9x_next')) is not None:
            return controller
        if len(self.controllers) > 2:  # More than 2 controller connected
            return '257'
        return '1'

    @cached_property
    def player3_device_type(self) -> str | None:
        return self.config.get('controller3_snes9x', '1')
