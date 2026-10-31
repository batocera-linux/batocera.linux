"""Controller input while the panel is open, read straight from evdev.

* Nothing is read while the panel is closed: hotkeygen opens it (see ``hotkey``).
* While the panel is open the pads are grabbed, so the game or EmulationStation does not also react;
  the guide button or the hotkey key closes it.
* Buttons are mapped by physical position (Linux gamepad spec) and by controller family, so Nintendo
  pads confirm with the right button (A) like on a Switch.
"""

from __future__ import annotations

import logging
import queue
import select
import threading
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final

import evdev
from evdev import ecodes

from .controls import Action, Family, detect_family
from .errors import IO_ERRORS

if TYPE_CHECKING:
    from collections.abc import Callable

_logger: Final = logging.getLogger(__name__)

REPEAT_DELAY: Final = 0.38
REPEAT_RATE: Final = 0.11
STICK_THRESHOLD: Final = 0.6


_COMMON: Final = {
    ecodes.BTN_TL: Action.PREV_TAB,
    ecodes.BTN_TR: Action.NEXT_TAB,
    ecodes.BTN_START: Action.START,
}
KEYMAPS: Final[dict[Family, dict[int, Action]]] = {
    Family.XBOX: {
        ecodes.BTN_SOUTH: Action.CONFIRM,
        ecodes.BTN_EAST: Action.BACK,
        ecodes.BTN_WEST: Action.MUTE,
        ecodes.BTN_NORTH: Action.DEAFEN,
        **_COMMON,
    },
    Family.PLAYSTATION: {
        ecodes.BTN_SOUTH: Action.CONFIRM,
        ecodes.BTN_EAST: Action.BACK,
        ecodes.BTN_WEST: Action.MUTE,
        ecodes.BTN_NORTH: Action.DEAFEN,
        **_COMMON,
    },
    Family.NINTENDO: {
        ecodes.BTN_EAST: Action.CONFIRM,
        ecodes.BTN_SOUTH: Action.BACK,
        ecodes.BTN_WEST: Action.MUTE,
        ecodes.BTN_NORTH: Action.DEAFEN,
        **_COMMON,
    },
}


def is_gamepad(keys: list[int], /) -> bool:
    return ecodes.BTN_SOUTH in keys and ecodes.BTN_MODE in keys


@dataclass(slots=True)
class _Pad:
    device: evdev.InputDevice[str]
    family: Family


@dataclass(slots=True)
class Pads:
    """Reads and grabs every gamepad while active (panel open, or Discord's consent dialog shown).

    ``actions`` receives navigation actions; ``on_close`` is called when one of ``close_keys`` is released.
    In pointer mode the left stick and d-pad move the X pointer instead.
    """

    on_close: Callable[[], None]
    close_keys: frozenset[int] = frozenset({ecodes.BTN_MODE})
    actions: queue.Queue[Action] = field(default_factory=queue.Queue[Action])
    last_family: Family = Family.XBOX
    pointer: Callable[[float, float], None] | None = None  # set while Discord's consent dialog is shown

    _pads: dict[str, _Pad] = field(default_factory=dict[str, _Pad])
    _active: bool = False
    _thread: threading.Thread | None = None
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _held: dict[Action, float] = field(default_factory=dict[Action, float])
    _stick: list[float] = field(default_factory=lambda: [0.0, 0.0])

    @property
    def active(self) -> bool:
        return self._active

    def set_active(self, on: bool, /) -> None:
        """Start reading and grabbing the pads, or give them back (done by the reader thread)."""
        with self._lock:
            self._active = on
            if on and (self._thread is None or not self._thread.is_alive()):
                self._thread = threading.Thread(target=self._loop, name='discord-pads', daemon=True)
                self._thread.start()

    def release(self) -> None:
        """Synchronously give the pads back, e.g. right before exiting."""
        with self._lock:
            self._active = False
        self._close_all()

    # -- device management --
    def _scan(self) -> None:
        for path in evdev.list_devices():
            if path in self._pads:
                continue
            try:
                device = evdev.InputDevice(path)
            except OSError:
                continue
            if not is_gamepad(device.capabilities().get(ecodes.EV_KEY, [])):
                device.close()
                continue
            family = detect_family(device.name, device.info.vendor)
            self._pads[path] = _Pad(device, family)
            if len(self._pads) == 1:
                self.last_family = family
            try:
                device.grab()
            except OSError:
                _logger.debug('cannot grab %s', device.path)
            _logger.debug('controller: %s (%s)', device.name, family)

    def _close_all(self) -> None:
        for pad in list(self._pads.values()):
            try:
                pad.device.ungrab()
            except OSError:
                pass
            pad.device.close()
        self._pads.clear()
        self._held.clear()

    # -- event handling --
    def _press(self, action: Action, active: bool, /) -> None:
        if active and action not in self._held:
            self.actions.put(action)
            self._held[action] = time.monotonic() + REPEAT_DELAY
        elif not active:
            self._held.pop(action, None)

    def handle(self, pad: _Pad, event: evdev.InputEvent, /) -> None:
        if event.type == ecodes.EV_KEY:
            if event.value == 1:
                self.last_family = pad.family
            if event.code in self.close_keys:
                if event.value == 0:
                    self.on_close()
            elif event.value == 1 and (action := KEYMAPS[pad.family].get(event.code)) is not None:
                self.actions.put(action)
        elif event.type == ecodes.EV_ABS:
            self._handle_axis(pad.device, event)

    def _handle_axis(self, device: evdev.InputDevice[str], event: evdev.InputEvent, /) -> None:
        code, value = event.code, event.value
        if code == ecodes.ABS_HAT0Y:
            self._press(Action.UP, value < 0)
            self._press(Action.DOWN, value > 0)
        elif code == ecodes.ABS_HAT0X:
            self._press(Action.LEFT, value < 0)
            self._press(Action.RIGHT, value > 0)
        elif code in (ecodes.ABS_X, ecodes.ABS_Y, ecodes.ABS_RY):
            info = device.absinfo(code)
            middle = (info.max + info.min) / 2
            norm = (value - middle) / (((info.max - info.min) / 2) or 1)
            if code == ecodes.ABS_RY:
                self._press(Action.SCROLL_UP, norm < -STICK_THRESHOLD)
                self._press(Action.SCROLL_DOWN, norm > STICK_THRESHOLD)
                return
            self._stick[0 if code == ecodes.ABS_X else 1] = norm
            if self.pointer is None:
                if code == ecodes.ABS_Y:
                    self._press(Action.UP, norm < -STICK_THRESHOLD)
                    self._press(Action.DOWN, norm > STICK_THRESHOLD)
                else:
                    self._press(Action.LEFT, norm < -STICK_THRESHOLD)
                    self._press(Action.RIGHT, norm > STICK_THRESHOLD)

    def _tick(self) -> None:
        now = time.monotonic()
        if self.pointer is not None:
            x, y = self._stick
            for action, dx, dy in (
                (Action.LEFT, -0.6, 0),
                (Action.RIGHT, 0.6, 0),
                (Action.UP, 0, -0.6),
                (Action.DOWN, 0, 0.6),
            ):
                if action in self._held:
                    x, y = x + dx, y + dy
            if abs(x) > 0.15 or abs(y) > 0.15:
                self.pointer(x, y)
            return
        for action, due in list(self._held.items()):
            if now >= due:
                self.actions.put(action)
                self._held[action] = now + REPEAT_RATE

    def _loop(self) -> None:
        last_scan = 0.0
        while True:
            with self._lock:
                if not self._active:
                    self._close_all()
                    self._thread = None
                    return
            if time.monotonic() - last_scan > 2:
                self._scan()
                last_scan = time.monotonic()
            self._tick()
            by_fd = {pad.device.fd: (path, pad) for path, pad in self._pads.items()}
            if not by_fd:
                time.sleep(0.25)
                continue
            try:
                ready, _, _ = select.select(list(by_fd), [], [], 0.03)
            except IO_ERRORS:
                ready = []
            for fd in ready:
                path, pad = by_fd[fd]
                try:
                    for event in pad.device.read():
                        self.handle(pad, event)
                except OSError:
                    _logger.info('controller removed: %s', path)
                    self._pads.pop(path, None)
