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

from batocera_common.power import apply_power_mode, global_power_mode, power_mode

from ..plugin_manager import HookContext, Plugin

if TYPE_CHECKING:
    from ..config.config import SystemConfig


def resolve_power_mode(config: SystemConfig, /) -> str:
    return power_mode(config.system_settings.get('powermode')) or global_power_mode(config.global_settings)


class PowerModePlugin(Plugin):
    def start(self, context: HookContext, /) -> None:
        apply_power_mode(resolve_power_mode(context.config))

    def stop(self, context: HookContext, /) -> None:
        apply_power_mode(global_power_mode(context.config.global_settings))
