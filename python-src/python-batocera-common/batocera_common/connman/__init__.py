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
