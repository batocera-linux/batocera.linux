from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import time
from contextlib import AbstractAsyncContextManager
from copy import deepcopy
from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final, Self

from batocera_common.asyncio import run
from batocera_common.paths import CONFIGS

if TYPE_CHECKING:
    from collections.abc import Sequence
    from types import TracebackType

    from ..config.config import UIMode
    from ..types import HotkeysContext

_logger = logging.getLogger(__name__)

_CONTEXT_FILE: Final = Path('/var/run/hotkeygen.context')
_PID_FILE: Final = Path('/var/run/hotkeygen.pid')
_COMMON_CONTEXT_FILES: Final = (
    Path('/etc/hotkeygen/common_context.conf'),
    CONFIGS / 'hotkeygen' / 'common_context.conf',
)


def _notify_daemon() -> None:
    os.kill(int(_PID_FILE.read_text().strip()), signal.SIGHUP)


def _set_context(context: HotkeysContext | None, /, *, include_common: bool = True) -> None:
    if context is None:
        _CONTEXT_FILE.unlink(missing_ok=True)
    else:
        from evdev import ecodes

        keys: dict[str, Sequence[str]] = dict(context['keys'])

        if include_common:
            for common_file in _COMMON_CONTEXT_FILES:
                if common_file.exists():
                    common_keys: dict[str, Sequence[str]] = json.loads(common_file.read_text())
                    keys |= common_keys

        for value in keys.values():
            names: Sequence[str]
            if isinstance(value, str):
                names = [value] if value.startswith('KEY_') else []
            else:
                names = value

            for name in names:
                if name not in ecodes.ecodes:
                    raise ValueError(f'invalid key {name!r}')

        tmp_file = _CONTEXT_FILE.with_suffix('.tmp')
        tmp_file.write_text(json.dumps({'name': context['name'], 'keys': keys}, indent=2))
        tmp_file.replace(_CONTEXT_FILE)

    _notify_daemon()


def _reset_mouse() -> None:
    import evdev
    from evdev import ecodes

    with evdev.UInput(
        name='batocera-mouse-reset',
        events={ecodes.EV_REL: [ecodes.REL_X, ecodes.REL_Y], ecodes.EV_KEY: [ecodes.BTN_LEFT]},
    ) as sender:
        time.sleep(0.2)

        sender.write(ecodes.EV_REL, ecodes.REL_X, -10000)
        sender.write(ecodes.EV_REL, ecodes.REL_Y, -10000)
        sender.syn()

        time.sleep(0.1)

        if os.environ.get('WAYLAND_DISPLAY'):
            sender.write(ecodes.EV_KEY, ecodes.BTN_LEFT, 1)
            sender.syn()
            sender.write(ecodes.EV_KEY, ecodes.BTN_LEFT, 0)
            sender.syn()

            time.sleep(0.1)


@dataclass(slots=True)
class HotkeygenManager(AbstractAsyncContextManager['HotkeygenManager', None]):
    _context: InitVar[HotkeysContext]
    exit_only: bool
    ui_mode: InitVar[UIMode]

    context: HotkeysContext = field(init=False)

    def __post_init__(self, _context: HotkeysContext, ui_mode: UIMode) -> None:
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

        try:
            _set_context(self.context, include_common=not self.exit_only)
        except Exception as e:
            _logger.warning('hotkeygen: direct context update failed (%s), using the cli', e)

            cmd = ['hotkeygen', '--new-context', self.context['name'], json.dumps(self.context['keys'])]

            if self.exit_only:
                cmd.append('--disable-common')

            await run(*cmd, capture_output=False)

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
        try:
            _set_context(None)
        except Exception as e:
            _logger.warning('hotkeygen: direct context reset failed (%s), using the cli', e)
            await run('hotkeygen', '--default-context', capture_output=False)


async def reset_mouse() -> None:
    try:
        _logger.debug('Triggering mouse reset to primary display')
        await asyncio.to_thread(_reset_mouse)
    except Exception as e:
        _logger.warning('Failed to reset mouse: %s', e)


def get_hotkeygen_event() -> str | None:
    import evdev

    for dev in evdev.list_devices():
        input_device = evdev.InputDevice(dev)
        if input_device.name == 'batocera hotkeys':
            return dev
    return None
