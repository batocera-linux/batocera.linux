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

# In-game menu for EKA2L1: hold hotkey alone for 3 seconds, then either press the pad button to change and
# pick its phone key, try the screen filters, applied as the cursor moves, for this session only (the ES
# option sets the game's filter), or search the game's memory for cheats (eka2l1_cheats.py; D-pad, A: confirm,
# B or hotkey: cancel). Started by eka2l1.py with a session file.

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

from batocera_launch.emulators.eka2l1 import (
    PAD_LABELS,
    REMAPPABLE,
    game_screen_filter,
    remap,
    save_game_pad_layout,
    save_game_screen_filter,
    screen_filters,
)
from batocera_launch.emulators.eka2l1_cheats import Cheats, Outcome, View, http_api

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
    'press': 'Press the pad button to change',
    'pick': 'Phone key for {button}',
    'press_hint': 'Hotkey: cancel',
    'pick_hint': 'D-pad: move   East: confirm   South: cancel',
    'saved': '{button} → {key}',
    'none': 'nothing',
    'menu': 'EKA2L1',
    'menu_keys': 'Change buttons',
    'menu_filter': 'Screen filter:  ◀ {filter} ▶',
    'menu_cheats': 'Cheats',
    'menu_hint': '▲ ▼: choose   ◀ ▶: filter   East: confirm   South: close',
    'filter': 'Screen filter {position}/{count}',
    'filter_hint': 'D-pad: try   East: keep   South: cancel',
    'filter_none': 'None',
    'filter_saved': 'Screen filter: {filter} (this session)',
}

# filter rows shown at once, the list scrolling with the cursor
_FILTER_ROWS: Final = 9


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
    MENU = auto()  # choosing between the pad keys and the screen filter
    PRESS = auto()  # waiting for the pad button to change
    PICK = auto()  # choosing its phone key
    FILTER = auto()  # choosing the screen filter, applied as the cursor moves
    CHEATS = auto()  # the cheats screens


class _Entry(Enum):
    KEYS = auto()
    FILTER = auto()
    CHEATS = auto()


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


def _step(direction: str, /) -> int:
    match direction:
        case 'up' | 'joystick1up':
            return -1
        case 'down' | 'joystick1down':
            return 1
        case 'left' | 'joystick1left':
            return -_FILTER_ROWS
        case 'right' | 'joystick1right':
            return _FILTER_ROWS
        case _:
            return 0


@dataclass(slots=True)
class _Remapper:
    rom: Path
    layout: list[tuple[str, str]]
    # the applications of the game, whose EKA2L1 settings hold the filter; none: no filter entry
    uids: list[int] = field(default_factory=list[int])
    # None: no shader
    filters: list[str | None] = field(default_factory=lambda: [None])
    stage: _Stage = _Stage.IDLE
    button: str | None = None
    cursor: tuple[int, int] = (5, 1)
    saved: tuple[str, str | None] | None = None
    armed_at: float = 0.0
    entry: _Entry = _Entry.KEYS
    filter: str | None = None  # the game's filter, as EKA2L1 shows it
    filter_before: str | None = None
    filter_cursor: int = 0
    saved_filter: bool = False
    # None: EKA2L1 has no control port, no cheats entry
    cheats: Cheats | None = None
    notice: str | None = None

    @property
    def has_filters(self) -> bool:
        return bool(self.uids) and len(self.filters) > 1

    @property
    def entries(self) -> list[_Entry]:
        return [
            _Entry.KEYS,
            *([_Entry.FILTER] if self.has_filters else []),
            *([_Entry.CHEATS] if self.cheats is not None else []),
        ]

    @property
    def has_menu(self) -> bool:
        return len(self.entries) > 1

    def _apply_filter(self, shader: str | None, /) -> None:
        if shader != self.filter:
            save_game_screen_filter(self.uids, shader)
            self.filter = shader

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
            case _Stage.MENU:
                if name in ('b', 'hotkey'):
                    self.stage = _Stage.IDLE
                elif name == 'a' and self.entry == _Entry.KEYS:
                    self.stage = _Stage.PRESS
                elif name == 'a' and self.entry == _Entry.CHEATS and self.cheats is not None:
                    if self.cheats.open():
                        self.stage = _Stage.CHEATS
                    else:
                        self.notice = self.cheats.error
                        self.stage = _Stage.IDLE
                elif name == 'a':
                    self.filter_before = self.filter
                    self.filter_cursor = self.filters.index(self.filter) if self.filter in self.filters else 0
                    self.stage = _Stage.FILTER
                elif (step := _step(name)) in (-1, 1):
                    entries = self.entries
                    index = entries.index(self.entry) if self.entry in entries else 0
                    self.entry = entries[(index + step) % len(entries)]
                elif step and self.entry == _Entry.FILTER:
                    # left and right go through the filters from the menu itself
                    index = self.filters.index(self.filter) if self.filter in self.filters else 0
                    self._apply_filter(self.filters[(index + (1 if step > 0 else -1)) % len(self.filters)])
            case _Stage.FILTER:
                if name in ('b', 'hotkey'):
                    self._apply_filter(self.filter_before)
                    self.stage = _Stage.IDLE
                elif name == 'a':
                    self._apply_filter(self.filters[self.filter_cursor])
                    self.saved_filter = True
                    self.stage = _Stage.IDLE
                elif step := _step(name):
                    last = len(self.filters) - 1
                    if abs(step) == 1:
                        self.filter_cursor = (self.filter_cursor + step) % len(self.filters)
                    else:
                        self.filter_cursor = min(max(self.filter_cursor + step, 0), last)
                    self._apply_filter(self.filters[self.filter_cursor])
            case _Stage.CHEATS if self.cheats is not None:
                match self.cheats.press(name):
                    case Outcome.CLOSE:
                        self.notice = self.cheats.notice
                        self.stage = _Stage.IDLE
                    case Outcome.BACK:
                        self.stage = _Stage.MENU
                    case Outcome.STAY:
                        pass
                self.cheats.notice = None
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
            self.stage = _Stage.MENU if self.has_menu else _Stage.PRESS

    def tick(self, now: float, /) -> None:
        if self.stage == _Stage.ARMED and now - self.armed_at >= _HOLD_SECONDS:
            self.stage = _Stage.HELD
            self.entry = _Entry.KEYS
            if self.has_filters:
                self.filter = game_screen_filter(self.uids)


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
        .item {{ background-color: #343840; border-radius: {px(10)}px; border: {px(2)}px solid #5c6370;
                 padding: {px(8)}px {px(18)}px; min-width: {px(300)}px; }}
        .item.cursor {{ background-color: #2896eb; border-color: #9fd2ff; }}
        .item.current {{ border-color: #f0c040; }}
        .item label {{ color: #eef2ff; font-size: {px(22)}px; }}
        .number {{ color: #eef2ff; font-size: {px(44)}px; font-family: monospace; }}
        .error {{ color: #ff9f80; }}
    """.encode()


def main(argv: Sequence[str], /) -> int:
    logging.basicConfig(level=logging.INFO)
    session = json.loads(Path(argv[1]).read_text())

    import evdev
    import gi

    gi.require_version('Gtk', '3.0')
    gi.require_version('Pango', '1.0')
    from gi.repository import GLib, Gtk, Pango

    device = evdev.InputDevice(session['device'])
    axes = {code: _AxisRange(info.min, info.max) for code, info in device.capabilities().get(_EV_ABS, [])}
    reader = _PadReader(_with_opposite_directions(_PadInput(*pad_input) for pad_input in session['inputs']), axes)
    remapper = _Remapper(
        Path(session['rom']),
        [(str(trigger), str(target)) for trigger, target in session['layout']],
        [int(uid) for uid in session.get('uids', [])],
        [None, *screen_filters()],
        cheats=Cheats(http_api(int(port))) if (port := session.get('control_port')) else None,
    )
    texts = _TEXTS
    scale = session.get('screen_height', 1080) / 1080
    margin = round(24 * scale)

    window = Gtk.Window(title='EKA2L1 pad', decorated=False, skip_taskbar_hint=True, skip_pager_hint=True)
    window.set_keep_above(True)
    if visual := window.get_screen().get_rgba_visual():
        window.set_visual(visual)
    layer_shell: Any = None
    try:
        # above the fullscreen game on Wayland (labwc), centred as no edge is anchored
        gi.require_version('GtkLayerShell', '0.1')
        layer_shell = cast('Any', importlib.import_module('gi.repository.GtkLayerShell'))
        layer_shell.init_for_window(window)
        layer_shell.set_layer(window, layer_shell.Layer.OVERLAY)
        layer_shell.set_keyboard_mode(window, layer_shell.KeyboardMode.NONE)
        layer_shell.set_margin(window, layer_shell.Edge.LEFT, margin)
    except ValueError, ImportError:
        layer_shell = None
        window.set_position(Gtk.WindowPosition.CENTER)

    def place(on_the_left: bool) -> None:
        # the filter list beside the game, which stays in sight, as wide whatever it shows
        panel.set_size_request(round(600 * scale) if on_the_left else -1, -1)
        if layer_shell is not None:
            layer_shell.set_anchor(window, layer_shell.Edge.LEFT, on_the_left)
        elif on_the_left:
            window.set_position(Gtk.WindowPosition.NONE)
            height = window.get_preferred_size()[1].height
            window.move(margin, max(0, (window.get_screen().get_height() - height) // 2))
        else:
            window.set_position(Gtk.WindowPosition.CENTER)

    provider = Gtk.CssProvider()
    provider.load_from_data(_css(scale))
    Gtk.StyleContext.add_provider_for_screen(window.get_screen(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=round(12 * scale))
    panel.get_style_context().add_class('panel')
    title = Gtk.Label()
    title.get_style_context().add_class('title')
    hint = Gtk.Label(wrap=True, max_width_chars=52, justify=Gtk.Justification.CENTER)
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
    grid.set_no_show_all(True)
    # the menu entries, or the filters around the cursor
    items = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=round(6 * scale))
    items.set_no_show_all(True)
    rows: list[tuple[Gtk.Box, Gtk.Label]] = []
    for _ in range(_FILTER_ROWS):
        item = Gtk.Box()
        item.get_style_context().add_class('item')
        # cut rather than widen the panel
        item_label = Gtk.Label(xalign=0, ellipsize=Pango.EllipsizeMode.END, max_width_chars=40)
        item.pack_start(item_label, True, True, 0)
        items.pack_start(item, False, False, 0)
        item_label.show()
        rows.append((item, item_label))
    # the value typed in the cheats, digit by digit
    number = Gtk.Label(halign=Gtk.Align.CENTER)
    number.get_style_context().add_class('number')
    number.set_no_show_all(True)
    panel.pack_start(title, False, False, 0)
    panel.pack_start(grid, False, False, 0)
    panel.pack_start(items, False, False, 0)
    panel.pack_start(number, False, False, 0)
    panel.pack_start(hint, False, False, 0)
    window.add(panel)

    def filter_name(shader: str | None) -> str:
        return texts['filter_none'] if shader is None else shader

    def show_items(entries: Sequence[tuple[str, bool, bool]]) -> None:
        # (text, under the cursor, current)
        for index, (item, item_label) in enumerate(rows):
            if index >= len(entries):
                item.hide()
                continue
            text, cursor, current = entries[index]
            item_label.set_text(text)
            context = item.get_style_context()
            (context.add_class if cursor else context.remove_class)('cursor')
            (context.add_class if current else context.remove_class)('current')
            item.show()
        grid.hide()
        number.hide()
        items.show()

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

    def show() -> None:
        window.show_all()
        # back to the size of what is shown now
        window.resize(1, 1)

    def refresh() -> None:
        stage = remapper.stage
        set_grab(stage in (_Stage.MENU, _Stage.PRESS, _Stage.PICK, _Stage.FILTER, _Stage.CHEATS))
        title.get_style_context().remove_class('error')
        if stage == _Stage.IDLE:
            if remapper.saved is not None or remapper.saved_filter or remapper.notice:
                if remapper.notice:
                    title.set_text(remapper.notice)
                    remapper.notice = None
                elif remapper.saved is not None:
                    button, key = remapper.saved
                    symbol = next((s for keys in _KEYPAD for k, s in keys if k == key), texts['none'])
                    title.set_text(texts['saved'].format(button=PAD_LABELS.get(button, button), key=symbol))
                else:
                    title.set_text(texts['filter_saved'].format(filter=filter_name(remapper.filter)))
                hint.set_text('')
                remapper.saved = None
                remapper.saved_filter = False
                grid.hide()
                items.hide()
                number.hide()
                show()
                GLib.timeout_add(1500, hide_later)
            else:
                window.hide()
            return
        if stage == _Stage.ARMED:
            return
        if stage == _Stage.HELD:
            stage = _Stage.MENU if remapper.has_menu else _Stage.PRESS

        if stage == _Stage.MENU:
            entry_texts = {
                _Entry.KEYS: texts['menu_keys'],
                _Entry.FILTER: texts['menu_filter'].format(filter=filter_name(remapper.filter)),
                _Entry.CHEATS: texts['menu_cheats'],
            }
            show_items([(entry_texts[entry], remapper.entry == entry, False) for entry in remapper.entries])
            title.set_text(texts['menu'])
            hint.set_text(texts['menu_hint'])
            # beside the game, which shows the filters tried from here
            place(on_the_left=True)
            show()
            return

        if stage == _Stage.CHEATS and remapper.cheats is not None:
            cheats = remapper.cheats
            heading, help_text, view, rows_shown = cheats.view()
            if view == View.NUMBER:
                number.set_markup(
                    ' '.join(
                        f'<span background="#2896eb">{digit}</span>' if cursor else digit
                        for digit, cursor in rows_shown
                    )
                )
                grid.hide()
                items.hide()
                number.show()
            else:
                show_items([(text, cursor, False) for text, cursor in rows_shown])
            if cheats.error:
                heading = cheats.error
                title.get_style_context().add_class('error')
            title.set_text(heading)
            hint.set_text(help_text)
            place(on_the_left=True)
            show()
            return

        if stage == _Stage.FILTER:
            count = len(remapper.filters)
            first = min(max(remapper.filter_cursor - _FILTER_ROWS // 2, 0), max(count - _FILTER_ROWS, 0))
            show_items(
                [
                    (filter_name(shader), index == remapper.filter_cursor, shader == remapper.filter_before)
                    for index, shader in enumerate(remapper.filters[first : first + _FILTER_ROWS], first)
                ]
            )
            title.set_text(texts['filter'].format(position=remapper.filter_cursor + 1, count=count))
            hint.set_text(texts['filter_hint'])
            place(on_the_left=True)
            show()
            return

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
        items.hide()
        number.hide()
        # show_all() does nothing on a widget kept out of the window's show_all()
        for child in grid.get_children():
            child.show_all()
        grid.show()
        place(on_the_left=False)
        show()

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
                if remapper.stage != before or remapper.stage in (
                    _Stage.MENU,
                    _Stage.PICK,
                    _Stage.FILTER,
                    _Stage.CHEATS,
                ):
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
