from __future__ import annotations

import json
import logging
from contextlib import AbstractAsyncContextManager
from dataclasses import InitVar, dataclass, field
from typing import TYPE_CHECKING, Self

from batocera_common.asyncio import run

if TYPE_CHECKING:
    from types import TracebackType

    from batocera_launch.emulator import Emulator
    from batocera_launch.types import HotkeysContext

_logger = logging.getLogger(__name__)


@dataclass(slots=True)
class HotkeygenManager(AbstractAsyncContextManager['HotkeygenManager', None]):
    context: HotkeysContext = field(init=False)
    exit_only: bool = field(init=False)

    emulator: InitVar[Emulator]

    def __post_init__(self, emulator: Emulator) -> None:
        self.context = emulator.hotkeygen_context
        self.exit_only = emulator.config.get_bool('exithotkeyonly')

        # limit hotkeys
        # there is an option to disable all hotkeys but exit in case the player 1 is a pad with not hotkey specific button
        if self.exit_only:
            if 'exit' in self.context['keys']:
                self.context['keys'] = {'exit': self.context['keys']['exit']}
            else:
                # should not happen while exit should always be there
                self.context['keys'] = {}

        # if uimod is not full (aka kiosk or children mode), remove the menu action
        if emulator.config.ui_mode != 'Full' and 'menu' in self.context['keys']:
            del self.context['keys']['menu']

    async def __aenter__(self) -> Self:
        _logger.debug('hotkeygen: updating context to %s', self.context['name'])

        cmd = ['hotkeygen', '--new-context', self.context['name'], json.dumps(self.context['keys'])]

        if self.exit_only:
            cmd.append('--disable-common')

        await run(*cmd)

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
        await run('hotkeygen', '--default-context')

    async def reset_mouse(self) -> None:
        try:
            _logger.debug('Triggering mouse reset to primary display')
            await run('/usr/bin/hotkeygen', '--reset-mouse')
        except Exception as e:
            _logger.warning('Failed to reset mouse: %s', e)


def get_hotkeygen_event() -> str | None:
    import evdev

    for dev in evdev.list_devices():
        input_device = evdev.InputDevice(dev)
        if input_device.name == 'batocera hotkeys':
            return dev
    return None
