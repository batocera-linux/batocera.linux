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

from batocera_common.fan import set_fan_profile

from ..plugin_manager import HookContext, Plugin


class FanPlugin(Plugin):
    def start(self, context: HookContext, /) -> None:
        if (profile := context.config.get_str('fanprofile')) is not None:
            set_fan_profile(profile)

    def stop(self, context: HookContext, /) -> None:
        # also undoes a change from the control center during the game
        set_fan_profile(context.config.global_settings.get('fanprofile'))
