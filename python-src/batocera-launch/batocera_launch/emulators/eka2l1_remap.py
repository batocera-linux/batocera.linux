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

# In-game pad remapping for EKA2L1: hold hotkey alone for 3 seconds, press the pad button to change,
# then pick its phone key (D-pad, A: confirm, B or hotkey: cancel). Started by eka2l1.py with a session file.

from __future__ import annotations

import importlib
import json
import logging
import signal
import sys
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, NamedTuple, cast

from batocera_launch.emulators.eka2l1 import PAD_LABELS, REMAPPABLE, remap, save_game_pad_layout

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

_logger = logging.getLogger(__name__)

_EV_KEY: Final = 0x01
_EV_ABS: Final = 0x03
_ABS_HAT0X: Final = 0x10

# the phone's keypad: (phone key, or None to unassign; symbol)
_KEYPAD: Final[tuple[tuple[tuple[str | None, str], ...], ...]] = (
    (('KEY_F1', '▬'), ('KEY_UP', '▲'), ('KEY_F2', '▬')),
    (('KEY_LEFT', '◀'), ('KEY_ENTER', 'OK'), ('KEY_RIGHT', '▶')),
    (('KEY_F3', '✆'), ('KEY_DOWN', '▼'), ('KEY_F4', '✆')),
    (('KEY_BACKSPACE', 'C'), (None, '∅'), ('KEY_LEFTSHIFT', '✎')),
    (('KEY_1', '1'), ('KEY_2', '2'), ('KEY_3', '3')),
    (('KEY_4', '4'), ('KEY_5', '5'), ('KEY_6', '6')),
    (('KEY_7', '7'), ('KEY_8', '8'), ('KEY_9', '9')),
    (('KEY_KPASTERISK', '*'), ('KEY_0', '0'), ('KEY_SLASH', '#')),
)

_TEXTS: Final = {
    'en': {
        'press': 'Press the pad button to change',
        'pick': 'Phone key for {button}',
        'press_hint': 'Hotkey: cancel',
        'pick_hint': 'D-pad: _move   A: confirm   B: cancel',
        'saved': '{button} → {key}',
        'none': 'nothing',
    },
    'fr': {
        'press': 'Appuie sur le bouton à changer',
        'pick': 'Touche du téléphone pour {button}',
        'press_hint': 'Hotkey : annuler',
        'pick_hint': 'Croix : choisir   A : valider   B : annuler',
        'saved': '{button} → {key}',
        'none': 'rien',
    },
}


class _PadInput(NamedTuple):
    name: str
    type: str
    id: str
    value: str
    code: str | None


_HOLD_SECONDS: Final = 3.0

_OPPOSITE_DIRECTIONS: Final = {'up': 'down', 'left': 'right'}


def _with_opposite_directions(inputs: Iterable[_PadInput], /) -> list[_PadInput]:
    # es_input.cfg only has the up and left of the sticks
    complete = list(inputs)
    names = {pad_input.name for pad_input in complete}
    for pad_input in list(complete):
        if pad_input.type != 'axis' or not pad_input.name.startswith('joystick'):
            continue
        for direction, opposite in _OPPOSITE_DIRECTIONS.items():
            name = pad_input.name.removesuffix(direction) + opposite
            if pad_input.name.endswith(direction) and name not in names:
                complete.append(pad_input._replace(name=name, value=str(-int(pad_input.value))))
    return complete


class _AxisRange(NamedTuple):
    minimum: int
    maximum: int


@dataclass(slots=True)
class _PadReader:
    inputs: Sequence[_PadInput]
    axes: Mapping[int, _AxisRange] = field(default_factory=dict[int, _AxisRange])
    pressed: set[str] = field(default_factory=set[str])

    def _is_active(self, pad_input: _PadInput, ev_type: int, code: int, value: int) -> bool | None:
        if pad_input.type == 'button' and ev_type == _EV_KEY and pad_input.code is not None:
            return value != 0 if code == int(pad_input.code) else None

        if pad_input.type == 'hat' and ev_type == _EV_ABS:
            hat_value = int(pad_input.value)
            is_y = hat_value in (1, 4)
            if code != _ABS_HAT0X + 2 * int(pad_input.id) + is_y:
                return None
            direction = -1 if hat_value in (1, 8) else 1
            return value == direction

        if pad_input.type == 'axis' and ev_type == _EV_ABS and pad_input.code is not None:
            if code != int(pad_input.code):
                return None
            axis = self.axes.get(code, _AxisRange(-32768, 32767))
            centre = (axis.minimum + axis.maximum) / 2
            half = (axis.maximum - axis.minimum) / 2 or 1
            direction = -1 if int(pad_input.value) < 0 else 1
            return (value - centre) * direction > half * 0.5

        return None

    def handle(self, ev_type: int, code: int, value: int) -> list[tuple[str, bool]]:
        changes: list[tuple[str, bool]] = []
        for pad_input in self.inputs:
            active = self._is_active(pad_input, ev_type, code, value)
            if active is None or active == (pad_input.name in self.pressed):
                continue
            if active:
                self.pressed.add(pad_input.name)
            else:
                self.pressed.discard(pad_input.name)
            changes.append((pad_input.name, active))
        return changes


class _Stage(Enum):
    IDLE = auto()
    ARMED = auto()  # hotkey held alone, not for long enough yet
    HELD = auto()  # held long enough: the screen shows, the pad is taken once hotkey is released
    PRESS = auto()  # waiting for the pad button to change
    PICK = auto()  # choosing its phone key


def _keypad_position(target: str | None, /) -> tuple[int, int]:
    for row, keys in enumerate(_KEYPAD):
        for column, (key, _) in enumerate(keys):
            if key == target:
                return row, column
    return 5, 1  # 5, the usual action key


def _move(position: tuple[int, int], direction: str, /) -> tuple[int, int]:
    row, column = position
    match direction:
        case 'up' | 'joystick1up':
            row = (row - 1) % len(_KEYPAD)
        case 'down' | 'joystick1down':
            row = (row + 1) % len(_KEYPAD)
        case 'left' | 'joystick1left':
            column = (column - 1) % 3
        case 'right' | 'joystick1right':
            column = (column + 1) % 3
        case _:
            pass
    return row, column


def _bound_buttons(layout: Iterable[tuple[str, str]], target: str | None, /) -> list[str]:
    return [PAD_LABELS.get(trigger, trigger) for trigger, key in layout if key == target]


@dataclass(slots=True)
class _Remapper:
    rom: Path
    layout: list[tuple[str, str]]
    stage: _Stage = _Stage.IDLE
    button: str | None = None
    cursor: tuple[int, int] = (5, 1)
    saved: tuple[str, str | None] | None = None
    armed_at: float = 0.0

    def press(self, name: str, pressed: set[str], now: float = 0.0, /) -> None:
        match self.stage:
            case _Stage.IDLE:
                # alone: hotkey with another button is one of the system shortcuts
                if pressed == {'hotkey'}:
                    self.stage = _Stage.ARMED
                    self.armed_at = now
            case _Stage.ARMED:
                self.stage = _Stage.IDLE
            case _Stage.HELD:
                pass
            case _Stage.PRESS:
                if name == 'hotkey':
                    self.stage = _Stage.IDLE
                elif name in REMAPPABLE:
                    self.button = name
                    current = next((key for trigger, key in self.layout if trigger == name), None)
                    self.cursor = _keypad_position(current)
                    self.stage = _Stage.PICK
            case _Stage.PICK:
                if name in ('b', 'hotkey'):
                    self.stage = _Stage.IDLE
                elif name == 'a' and self.button is not None:
                    target = _KEYPAD[self.cursor[0]][self.cursor[1]][0]
                    self.layout = remap(self.layout, self.button, target)
                    save_game_pad_layout(self.rom, self.layout)
                    self.saved = (self.button, target)
                    self.stage = _Stage.IDLE
                else:
                    self.cursor = _move(self.cursor, name)

    def release(self, pressed: set[str], /) -> None:
        if 'hotkey' in pressed:
            return
        if self.stage == _Stage.ARMED:
            self.stage = _Stage.IDLE
        elif self.stage == _Stage.HELD:
            # the system saw hotkey go up before the pad is taken, so it is not left held
            self.stage = _Stage.PRESS

    def tick(self, now: float, /) -> None:
        if self.stage == _Stage.ARMED and now - self.armed_at >= _HOLD_SECONDS:
            self.stage = _Stage.HELD


def _texts(language: str, /) -> Mapping[str, str]:
    return _TEXTS.get(language[:2].lower(), _TEXTS['en'])


def _css(scale: float, /) -> bytes:
    def px(size: float) -> int:
        return max(1, round(size * scale))

    return f"""
        window {{ background-color: transparent; }}
        .panel {{ background-color: rgba(20, 22, 26, 0.94); border-radius: {px(18)}px;
                  border: {px(2)}px solid #5a6270; padding: {px(18)}px; }}
        .title {{ color: #ffffff; font-size: {px(26)}px; font-weight: bold; }}
        .hint {{ color: #9fb3c8; font-size: {px(16)}px; }}
        .key {{ background-color: #343840; border-radius: {px(10)}px; border: {px(2)}px solid #5c6370;
                min-width: {px(118)}px; min-height: {px(62)}px; }}
        .key.cursor {{ background-color: #2896eb; border-color: #9fd2ff; }}
        .key.current {{ border-color: #f0c040; }}
        .symbol {{ color: #eef2ff; font-size: {px(24)}px; font-weight: bold; }}
        .pads {{ color: #9fd0ff; font-size: {px(12)}px; }}
    """.encode()


def main(argv: Sequence[str], /) -> int:
    logging.basicConfig(level=logging.INFO)
    session = json.loads(Path(argv[1]).read_text())

    import evdev
    import gi

    gi.require_version('Gtk', '3.0')
    from gi.repository import GLib, Gtk

    device = evdev.InputDevice(session['device'])
    axes = {code: _AxisRange(info.min, info.max) for code, info in device.capabilities().get(_EV_ABS, [])}
    reader = _PadReader(_with_opposite_directions(_PadInput(*pad_input) for pad_input in session['inputs']), axes)
    remapper = _Remapper(Path(session['rom']), [(str(trigger), str(target)) for trigger, target in session['layout']])
    texts = _texts(session.get('language', 'en'))
    scale = session.get('screen_height', 1080) / 1080

    window = Gtk.Window(title='EKA2L1 pad', decorated=False, skip_taskbar_hint=True, skip_pager_hint=True)
    window.set_keep_above(True)
    if visual := window.get_screen().get_rgba_visual():
        window.set_visual(visual)
    try:
        # above the fullscreen game on Wayland (labwc), centred as no edge is anchored
        gi.require_version('GtkLayerShell', '0.1')
        layer_shell = cast('Any', importlib.import_module('gi.repository.GtkLayerShell'))
        layer_shell.init_for_window(window)
        layer_shell.set_layer(window, layer_shell.Layer.OVERLAY)
        layer_shell.set_keyboard_mode(window, layer_shell.KeyboardMode.NONE)
    except ValueError, ImportError:
        window.set_position(Gtk.WindowPosition.CENTER)

    provider = Gtk.CssProvider()
    provider.load_from_data(_css(scale))
    Gtk.StyleContext.add_provider_for_screen(window.get_screen(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=round(12 * scale))
    panel.get_style_context().add_class('panel')
    title = Gtk.Label()
    title.get_style_context().add_class('title')
    hint = Gtk.Label()
    hint.get_style_context().add_class('hint')
    grid = Gtk.Grid(row_spacing=round(8 * scale), column_spacing=round(8 * scale), halign=Gtk.Align.CENTER)
    cells: dict[tuple[int, int], tuple[Gtk.Box, Gtk.Label]] = {}
    for row, keys in enumerate(_KEYPAD):
        for column, (_, symbol) in enumerate(keys):
            cell = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, valign=Gtk.Align.CENTER)
            cell.get_style_context().add_class('key')
            symbol_label = Gtk.Label(label=symbol)
            symbol_label.get_style_context().add_class('symbol')
            pads_label = Gtk.Label()
            pads_label.get_style_context().add_class('pads')
            cell.pack_start(symbol_label, True, True, 0)
            cell.pack_start(pads_label, False, False, 0)
            grid.attach(cell, column, row, 1, 1)
            cells[row, column] = (cell, pads_label)
    panel.pack_start(title, False, False, 0)
    panel.pack_start(grid, False, False, 0)
    panel.pack_start(hint, False, False, 0)
    window.add(panel)

    grabbed = False

    def set_grab(grab: bool) -> None:
        nonlocal grabbed
        if grab == grabbed:
            return
        try:
            device.grab() if grab else device.ungrab()
            grabbed = grab
        except OSError:
            _logger.warning('Unable to %s the pad', 'grab' if grab else 'release', exc_info=True)

    def hide_later() -> bool:
        if remapper.stage == _Stage.IDLE:
            window.hide()
        return False

    def refresh() -> None:
        stage = remapper.stage
        set_grab(stage in (_Stage.PRESS, _Stage.PICK))
        if stage == _Stage.IDLE:
            if remapper.saved is not None:
                button, key = remapper.saved
                symbol = next((s for keys in _KEYPAD for k, s in keys if k == key), texts['none'])
                title.set_text(texts['saved'].format(button=PAD_LABELS.get(button, button), key=symbol))
                hint.set_text('')
                remapper.saved = None
                GLib.timeout_add(1200, hide_later)
            else:
                window.hide()
            return
        if stage == _Stage.ARMED:
            return
        if stage == _Stage.HELD:
            stage = _Stage.PRESS

        for (row, column), (cell, pads_label) in cells.items():
            key = _KEYPAD[row][column][0]
            pads_label.set_text(' '.join(_bound_buttons(remapper.layout, key)))
            context = cell.get_style_context()
            for css_class, on in (
                ('cursor', stage == _Stage.PICK and (row, column) == remapper.cursor),
                (
                    'current',
                    stage == _Stage.PICK and any(t == remapper.button and k == key for t, k in remapper.layout),
                ),
            ):
                (context.add_class if on else context.remove_class)(css_class)

        button = PAD_LABELS.get(remapper.button or '', '')
        title.set_text(texts['press'] if stage == _Stage.PRESS else texts['pick'].format(button=button))
        hint.set_text(texts['press_hint'] if stage == _Stage.PRESS else texts['pick_hint'])
        window.show_all()

    def on_events(_channel: GLib.IOChannel, _condition: GLib.IOCondition) -> bool:
        try:
            events = list(device.read())
        except BlockingIOError:
            return True
        except OSError:
            _logger.warning('The pad is gone', exc_info=True)
            Gtk.main_quit()
            return False

        for event in events:
            for name, active in reader.handle(event.type, event.code, event.value):
                before = remapper.stage
                if active:
                    remapper.press(name, reader.pressed, time.monotonic())
                else:
                    remapper.release(reader.pressed)
                if remapper.stage == _Stage.ARMED and before != _Stage.ARMED:
                    GLib.timeout_add(round(_HOLD_SECONDS * 1000) + 50, on_hold)
                if remapper.stage != before or remapper.stage == _Stage.PICK:
                    refresh()
        return True

    def on_hold() -> bool:
        # a timer from an earlier, shorter hold finds the hold restarted and does nothing
        before = remapper.stage
        remapper.tick(time.monotonic())
        if remapper.stage != before:
            refresh()
        return False

    def on_terminate() -> bool:
        Gtk.main_quit()
        return False

    GLib.io_add_watch(
        GLib.IOChannel.unix_new(device.fd),
        GLib.PRIORITY_DEFAULT,
        # pygobject-stubs types this condition as an IOChannel
        GLib.IOCondition.IN | GLib.IOCondition.HUP | GLib.IOCondition.ERR,  # pyright: ignore[reportArgumentType]
        on_events,
    )
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, on_terminate)
    try:
        Gtk.main()
    finally:
        set_grab(False)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
