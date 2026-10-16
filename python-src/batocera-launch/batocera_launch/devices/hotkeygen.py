from __future__ import annotations

import logging
from contextlib import AbstractAsyncContextManager
from copy import deepcopy
from dataclasses import InitVar, dataclass, field
from typing import TYPE_CHECKING, Self

from hotkeygen.dbus.client import HotkeygenClient
from hotkeygen.paths import DEVICE_NAME

if TYPE_CHECKING:
    from types import TracebackType

    from batocera_common.dbus import Bus

    from ..config.config import UIMode
    from ..types import HotkeysContext

_logger = logging.getLogger(__name__)


@dataclass(slots=True)
class HotkeygenManager(AbstractAsyncContextManager['HotkeygenManager', None]):
    bus: InitVar[Bus]
    _context: InitVar[HotkeysContext]
    exit_only: bool
    ui_mode: InitVar[UIMode]

    context: HotkeysContext = field(init=False)
    dbus_client: HotkeygenClient = field(init=False)

    def __post_init__(self, bus: Bus, _context: HotkeysContext, ui_mode: UIMode) -> None:
        self.dbus_client = HotkeygenClient(bus)
        self.context = deepcopy(_context)

        # limit hotkeys
        # there is an option to disable all hotkeys but exit in case the player 1 is a pad with not hotkey specific button
        if self.exit_only:
            if 'exit' in self.context['keys']:
                self.context['keys'] = {'exit': self.context['keys']['exit']}
            else:
                # should not happen while exit should always be there
                self.context['keys'] = {}

        # if uimod is not full (aka kiosk or children mode), remove the menu action
        if ui_mode != 'Full' and 'menu' in self.context['keys']:
            del self.context['keys']['menu']

    async def __aenter__(self) -> Self:
        _logger.debug('hotkeygen: updating context to %s', self.context['name'])

        await self.dbus_client.set_context(
            {'name': self.context['name'], 'keys': self.context['keys']}, not self.exit_only
        )

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> None:
        # reset hotkeygen context
        _logger.debug('hotkeygen: resetting to default context')

        await self.dbus_client.set_default_context()


def get_hotkeygen_event() -> str | None:
    import evdev

    for dev in evdev.list_devices():
        input_device = evdev.InputDevice(dev)
        if input_device.name == DEVICE_NAME:
            return dev
    return None
