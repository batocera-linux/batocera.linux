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

import logging
from typing import TYPE_CHECKING, Literal

from .common import CONNMAN_BUS_NAME, CONNMAN_MANAGER_PATH
from .proxies import ConnmanManagerInterfaceProxy

if TYPE_CHECKING:
    from batocera_common.dbus import Bus

_logger = logging.getLogger(__name__)


async def is_connected(bus: Bus, /) -> bool:
    manager_object = bus.get_object(CONNMAN_BUS_NAME, CONNMAN_MANAGER_PATH)
    manager_proxy = manager_object.get_proxy(ConnmanManagerInterfaceProxy)

    try:
        properties = await manager_proxy.get_properties()
    except Exception:
        _logger.exception('Unable to get the connman connection state')
        return False

    if (state_object := properties.get('State')) is None:
        return False

    state: Literal['online', 'ready', 'offline', 'idle'] = state_object.value

    _logger.debug('state: %s', state)

    return state in ('online', 'ready')
