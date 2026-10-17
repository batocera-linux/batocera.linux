"""Controller input read straight from evdev.

* A lone press of the guide button (Xbox / PS / Home) toggles the overlay, so Hotkey combos keep working.
* While the overlay is open the pads are grabbed, so the game or EmulationStation does not also react.
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

LONE_PRESS_MAX: Final = 0.8  # seconds: a longer guide press is not a toggle
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
    """Reads every gamepad. ``actions`` receives navigation actions while ``grabbed``; ``on_toggle`` is
    called on a lone guide press. In pointer mode the left stick and d-pad move the X pointer instead."""

    on_toggle: Callable[[], None]
    guide_enabled: bool = True
    actions: queue.Queue[Action] = field(default_factory=queue.Queue[Action])
    last_family: Family = Family.XBOX
    pointer: Callable[[float, float], None] | None = None  # set while Discord's consent dialog is shown

    _pads: dict[str, _Pad] = field(default_factory=dict[str, _Pad])
    _grabbed: bool = False
    _want_grab: bool = False
    _guide_down: float | None = None
    _guide_other: bool = False
    _held: dict[Action, float] = field(default_factory=dict[Action, float])
    _stick: list[float] = field(default_factory=lambda: [0.0, 0.0])

    def start(self) -> None:
        threading.Thread(target=self._loop, name='discord-pads', daemon=True).start()

    def grab(self, on: bool, /) -> None:
        """Request exclusive access to the pads (applied by the reader thread)."""
        self._want_grab = on

    def release(self) -> None:
        """Synchronously give the pads back, e.g. right before exiting."""
        self._want_grab = False
        self._apply_grab(False)

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
            if self._grabbed:
                self._grab_one(device)
            _logger.info('controller: %s (%s)', device.name, family)

    def _grab_one(self, device: evdev.InputDevice[str], /) -> None:
        try:
            device.grab()
        except OSError:
            _logger.debug('cannot grab %s', device.path)

    def _apply_grab(self, on: bool, /) -> None:
        if on == self._grabbed:
            return
        self._grabbed = on
        for pad in list(self._pads.values()):
            if on:
                self._grab_one(pad.device)
            else:
                try:
                    pad.device.ungrab()
                except OSError:
                    pass
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
            if event.code == ecodes.BTN_MODE:
                self._handle_guide(event.value)
                return
            if self._guide_down is not None:
                self._guide_other = True
            if self._grabbed and event.value == 1 and (action := KEYMAPS[pad.family].get(event.code)) is not None:
                self.actions.put(action)
        elif event.type == ecodes.EV_ABS:
            if self._guide_down is not None and event.code in (ecodes.ABS_HAT0X, ecodes.ABS_HAT0Y) and event.value:
                self._guide_other = True
            if self._grabbed:
                self._handle_axis(pad.device, event)

    def _handle_guide(self, value: int, /) -> None:
        if value == 1:
            self._guide_down, self._guide_other = time.monotonic(), False
        elif value == 0 and self._guide_down is not None:
            lone = not self._guide_other and time.monotonic() - self._guide_down < LONE_PRESS_MAX
            self._guide_down = None
            if lone and (self.guide_enabled or self._grabbed):
                self.on_toggle()

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
            if time.monotonic() - last_scan > 2:
                self._scan()
                last_scan = time.monotonic()
            self._apply_grab(self._want_grab)
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
