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

# Cheats screens of the EKA2L1 in-game menu, in the way of Sorcerer on S60: search the game's memory for a value,
# narrow the results down as it changes, then keep, change and freeze the right one. EKA2L1 does the work through
# its control API (/v1/cheats) and keeps the codes of each game.

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Final, Protocol

_TEXTS: Final = {
    'title': 'Cheats',
    'title_app': 'Cheats: {app}',
    'new': 'New search',
    'next': 'Continue search  ({count} results)',
    'next_unknown': 'Continue search  (value unknown)',
    'results': 'Results  ({count})',
    'reset': 'Reset search',
    'codes': 'Codes  ({count})',
    'home_hint': '▲ ▼: choose   East: confirm   South: back',
    'new_title': 'New search',
    'next_title': 'Continue search',
    'size': 'Size:  ◀ {bits}-bit ▶',
    'compare': 'Value is:  ◀ {compare} ▶',
    'value': 'Value:  {value}',
    'search_value': 'Value:  ◀ {value} ▶',
    'unknown': '?',
    'go': 'Search',
    'form_hint': '▲ ▼: choose   ◀ ▶: change   East: confirm   South: back',
    'number_title': 'Value ({bits}-bit, up to {maximum})',
    'number_hint': '◀ ▶: digit   ▲ ▼: change   East: confirm   South: cancel',
    'found': '{count} results',
    'found_one': '1 result',
    'found_none': 'No result: start a new search',
    'too_many': 'Too many results ({count}): continue the search first',
    'results_title': 'Results {position}/{count}',
    'result': '{address}   {value}   (was {previous})',
    'result_gone': '{address}   gone',
    'results_hint': '▲ ▼: choose   ◀ ▶: page   East: add to codes   South: back',
    'codes_title': 'Codes',
    'restore': 'Freeze the saved codes again ({count})',
    'code': '{address}   {bits}-bit   {value}{frozen}',
    'code_frozen': '   ❄',
    'code_saved': '   (was frozen)',
    'no_code': 'No code yet: add one from the results',
    'codes_hint': '▲ ▼: choose   East: open   South: back',
    'code_title': 'Code {address}',
    'freeze': 'Frozen:  ◀ {state} ▶',
    'on': 'yes',
    'off': 'no',
    'remove': 'Remove',
    'code_hint': '▲ ▼: choose   ◀ ▶: change   East: confirm   South: back',
    'removed': 'Code {address} removed',
    'unreachable': 'EKA2L1 does not answer',
}

# against the value typed, or against the value at the previous search
_COMPARES: Final = (
    ('equal', 'equal to'),
    ('different', 'different from'),
    ('decreased', 'lower than before'),
    ('increased', 'higher than before'),
    ('not-increased', 'lower than or equal to before'),
    ('not-decreased', 'higher than or equal to before'),
    ('changed', 'changed'),
    ('unchanged', 'unchanged'),
)

_WIDTHS: Final = (1, 2, 4)
_DIGITS: Final = {1: 3, 2: 5, 4: 10}
# results listed at most, beyond that the search goes on first
_MAX_RESULTS: Final = 1000
ROWS: Final = 9


class CheatError(Exception):
    pass


class Api(Protocol):
    def __call__(self, method: str, path: str, body: dict[str, Any] | None = None, /) -> dict[str, Any]: ...


def http_api(port: int, /) -> Api:
    def call(method: str, path: str, body: dict[str, Any] | None = None, /) -> dict[str, Any]:
        data = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(f'http://127.0.0.1:{port}/v1/cheats{path}', data=data, method=method)
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as error:
            try:
                message = json.loads(error.read())['error']['message']
            except ValueError, KeyError, TypeError:
                message = str(error)
            raise CheatError(message) from error
        except OSError as error:
            raise CheatError(_TEXTS['unreachable']) from error

    return call


class Screen(Enum):
    HOME = auto()
    NEW = auto()
    NEXT = auto()
    NUMBER = auto()
    RESULTS = auto()
    CODES = auto()
    CODE = auto()


class Outcome(Enum):
    STAY = auto()
    BACK = auto()  # to the in-game menu
    CLOSE = auto()  # back to the game, with a notice


class View(Enum):
    LIST = auto()
    NUMBER = auto()


def _direction(name: str, /) -> str | None:
    match name:
        case 'up' | 'joystick1up':
            return 'up'
        case 'down' | 'joystick1down':
            return 'down'
        case 'left' | 'joystick1left':
            return 'left'
        case 'right' | 'joystick1right':
            return 'right'
        case _:
            return None


def _hex(address: int, /) -> str:
    return f'0x{address:08X}'


@dataclass(slots=True)
class Cheats:
    api: Api
    screen: Screen = Screen.HOME
    state: dict[str, Any] = field(default_factory=dict[str, Any])
    cursors: dict[Screen, int] = field(default_factory=dict[Screen, int])
    width: int = 4
    # '?': the value is not known, the search starts from a copy of the memory
    unknown: bool = True
    compare: str = 'equal'
    value: int = 0
    results: list[dict[str, Any]] = field(default_factory=list[dict[str, Any]])
    code: int = 0
    # the value being typed digit by digit, the digit under the cursor, and the screen it belongs to
    digits: list[int] = field(default_factory=list[int])
    digit: int = 0
    number_for: Screen = Screen.NEW
    error: str | None = None
    notice: str | None = None

    # --- state

    @property
    def search(self) -> dict[str, Any]:
        return self.state.get('search', {})

    @property
    def codes(self) -> list[dict[str, Any]]:
        return self.state.get('codes', [])

    def _call(self, method: str, path: str = '', body: dict[str, Any] | None = None, /) -> dict[str, Any] | None:
        try:
            answer = self.api(method, path, body)
        except CheatError as error:
            self.error = str(error)
            return None
        self.error = None
        if 'codes' in answer:
            self.state = answer
        return answer

    def open(self) -> bool:
        self.screen = Screen.HOME
        self.cursors.clear()
        return self._call('GET') is not None

    def _cursor(self) -> int:
        return self.cursors.get(self.screen, 0)

    def _home_entries(self) -> list[str]:
        entries = ['new']
        if self.search.get('active'):
            entries.append('next')
            if not self.search.get('unknown'):
                entries.append('results')
            entries.append('reset')
        entries.append('codes')
        return entries

    def _form_entries(self) -> list[str]:
        if self.screen == Screen.NEW:
            return ['size', 'value', 'go']
        needs_value = self.compare in ('equal', 'different')
        return ['compare', *(['value'] if needs_value else []), 'go']

    def _code_entries(self) -> list[str]:
        restore = sum(1 for code in self.codes if code.get('wasFrozen'))
        return [*(['restore'] if restore else []), *(f'code{index}' for index in range(len(self.codes)))]

    def _count(self) -> int:
        return len(
            {
                Screen.HOME: self._home_entries,
                Screen.NEW: self._form_entries,
                Screen.NEXT: self._form_entries,
                Screen.RESULTS: lambda: self.results,
                Screen.CODES: self._code_entries,
                Screen.CODE: lambda: ['value', 'freeze', 'remove'],
            }.get(self.screen, list)()
        )

    def _number(self, value: int, back: Screen, /) -> None:
        count = _DIGITS[self.width if back != Screen.CODE else self.codes[self.code]['width']]
        self.digits = [int(digit) for digit in str(value).zfill(count)[-count:]]
        self.digit = count - 1
        self.number_for = back
        self.screen = Screen.NUMBER

    def _number_width(self) -> int:
        return self.codes[self.code]['width'] if self.number_for == Screen.CODE else self.width

    def _found(self, answer: dict[str, Any] | None, /) -> Outcome:
        if answer is None:
            return Outcome.STAY
        count = int(answer['search']['count'])
        if answer['search'].get('unknown'):
            # a copy of the memory: the comparisons come next
            self.notice = _TEXTS['found'].format(count=count)
        elif count == 0:
            self.notice = _TEXTS['found_none']
        else:
            self.notice = _TEXTS['found_one'] if count == 1 else _TEXTS['found'].format(count=count)
        return Outcome.CLOSE

    def _open_results(self) -> None:
        count = int(self.search.get('count', 0))
        if count > _MAX_RESULTS:
            self.error = _TEXTS['too_many'].format(count=count)
            return
        if (answer := self._call('GET', f'/search/results?limit={_MAX_RESULTS}')) is None:
            return
        self.results = answer['results']
        self.screen = Screen.RESULTS
        self.cursors[Screen.RESULTS] = 0

    # --- input

    def press(self, name: str, /) -> Outcome:
        if name == 'hotkey':
            return Outcome.CLOSE
        direction = _direction(name)
        if self.screen == Screen.NUMBER:
            return self._press_number(name, direction)

        if name == 'b':
            self.error = None
            match self.screen:
                case Screen.HOME:
                    return Outcome.BACK
                case Screen.CODE:
                    self.screen = Screen.CODES
                case _:
                    self.screen = Screen.HOME
            self._call('GET')
            return Outcome.STAY

        count = self._count()
        if direction in ('up', 'down') and count:
            step = -1 if direction == 'up' else 1
            self.cursors[self.screen] = (self._cursor() + step) % count
            return Outcome.STAY

        match self.screen:
            case Screen.HOME:
                return self._press_home(name)
            case Screen.NEW | Screen.NEXT:
                return self._press_form(name, direction)
            case Screen.RESULTS:
                return self._press_results(name, direction)
            case Screen.CODES:
                return self._press_codes(name)
            case Screen.CODE:
                return self._press_code(name, direction)
            case _:
                return Outcome.STAY

    def _press_home(self, name: str, /) -> Outcome:
        if name != 'a':
            return Outcome.STAY
        entry = self._home_entries()[min(self._cursor(), len(self._home_entries()) - 1)]
        match entry:
            case 'new':
                self.screen = Screen.NEW
            case 'next':
                self.screen = Screen.NEXT
                self.width = int(self.search.get('width') or self.width)
                if self.search.get('unknown') and self.compare in ('equal', 'different'):
                    self.compare = 'decreased'
            case 'results':
                self._open_results()
            case 'reset':
                self._call('DELETE', '/search')
                self.cursors[Screen.HOME] = 0
            case 'codes':
                self.screen = Screen.CODES
            case _:
                pass
        return Outcome.STAY

    def _press_form(self, name: str, direction: str | None, /) -> Outcome:
        entries = self._form_entries()
        entry = entries[min(self._cursor(), len(entries) - 1)]
        step = 1 if direction == 'right' else -1 if direction == 'left' else 0
        match entry:
            case 'size' if step:
                self.width = _WIDTHS[(_WIDTHS.index(self.width) + step) % len(_WIDTHS)]
                self.value = min(self.value, (1 << (8 * self.width)) - 1)
            case 'value' if step and self.screen == Screen.NEW:
                # '?' first, then the value
                self.unknown = not self.unknown
            case 'compare' if step:
                names = [key for key, _ in _COMPARES]
                self.compare = names[(names.index(self.compare) + step) % len(names)]
                self.cursors[self.screen] = 0
            case 'value' if name == 'a':
                self._number(self.value, self.screen)
            case 'go' if name == 'a':
                if self.screen == Screen.NEW:
                    body: dict[str, Any] = {'width': self.width}
                    if not self.unknown:
                        body['value'] = self.value
                    return self._found(self._call('POST', '/search', body))
                return self._found(self._call('POST', '/search/next', {'compare': self.compare, 'value': self.value}))
            case _:
                pass
        return Outcome.STAY

    def _press_number(self, name: str, direction: str | None, /) -> Outcome:
        back = self.number_for
        match name, direction:
            case 'b', _:
                self.screen = back
            case 'a', _:
                value = min(int(''.join(map(str, self.digits))), (1 << (8 * self._number_width())) - 1)
                self.screen = back
                if back == Screen.CODE:
                    self._call('PATCH', f'/codes/{self.code}', {'value': value})
                else:
                    # a value typed replaces the '?'
                    self.value = value
                    self.unknown = False
                    self.cursors[back] = len(self._form_entries()) - 1  # on Search
            case _, 'left':
                self.digit = (self.digit - 1) % len(self.digits)
            case _, 'right':
                self.digit = (self.digit + 1) % len(self.digits)
            case _, 'up':
                self.digits[self.digit] = (self.digits[self.digit] + 1) % 10
            case _, 'down':
                self.digits[self.digit] = (self.digits[self.digit] - 1) % 10
            case _:
                pass
        return Outcome.STAY

    def _press_results(self, name: str, direction: str | None, /) -> Outcome:
        if not self.results:
            return Outcome.STAY
        if direction in ('left', 'right'):
            step = ROWS if direction == 'right' else -ROWS
            self.cursors[Screen.RESULTS] = min(max(self._cursor() + step, 0), len(self.results) - 1)
        elif name == 'a':
            address = self.results[self._cursor()]['address']
            width = int(self.search.get('width') or self.width)
            if (answer := self._call('POST', '/codes', {'address': address, 'width': width})) is not None:
                self.code = next(
                    (
                        i
                        for i, code in enumerate(answer['codes'])
                        if code['address'] == address and code['width'] == width
                    ),
                    len(self.codes) - 1,
                )
                self.screen = Screen.CODE
                self.cursors[Screen.CODE] = 0
        return Outcome.STAY

    def _press_codes(self, name: str, /) -> Outcome:
        entries = self._code_entries()
        if name != 'a' or not entries:
            return Outcome.STAY
        entry = entries[min(self._cursor(), len(entries) - 1)]
        if entry == 'restore':
            self._call('POST', '/codes/restore')
            self.cursors[Screen.CODES] = 0
        else:
            self.code = int(entry.removeprefix('code'))
            self.screen = Screen.CODE
            self.cursors[Screen.CODE] = 0
        return Outcome.STAY

    def _press_code(self, name: str, direction: str | None, /) -> Outcome:
        if self.code >= len(self.codes):
            self.screen = Screen.CODES
            return Outcome.STAY
        code = self.codes[self.code]
        match ('value', 'freeze', 'remove')[self._cursor()]:
            case 'value' if name == 'a':
                self._number(int(code['value']), Screen.CODE)
            case 'freeze' if name == 'a' or direction in ('left', 'right'):
                self._call('PATCH', f'/codes/{self.code}', {'frozen': not code['frozen']})
            case 'remove' if name == 'a':
                if self._call('DELETE', f'/codes/{self.code}') is not None:
                    self.notice = _TEXTS['removed'].format(address=_hex(code['address']))
                    self.screen = Screen.CODES
                    self.cursors[Screen.CODES] = 0
            case _:
                pass
        return Outcome.STAY

    # --- what the menu shows: title, hint, and either rows (text, under the cursor) or the digits

    def view(self) -> tuple[str, str, View, list[tuple[str, bool]]]:
        cursor = self._cursor()

        def rows(texts: list[str], /) -> list[tuple[str, bool]]:
            # the rows around the cursor
            first = min(max(cursor - ROWS // 2, 0), max(len(texts) - ROWS, 0))
            return [(text, index == cursor) for index, text in enumerate(texts[first : first + ROWS], first)]

        app = (self.state.get('app') or {}).get('name')
        match self.screen:
            case Screen.HOME:
                count = self.search.get('count', 0)
                texts = {
                    'new': _TEXTS['new'],
                    'next': _TEXTS['next_unknown']
                    if self.search.get('unknown')
                    else _TEXTS['next'].format(count=count),
                    'results': _TEXTS['results'].format(count=count),
                    'reset': _TEXTS['reset'],
                    'codes': _TEXTS['codes'].format(count=len(self.codes)),
                }
                title = _TEXTS['title_app'].format(app=app) if app else _TEXTS['title']
                return title, _TEXTS['home_hint'], View.LIST, rows([texts[e] for e in self._home_entries()])
            case Screen.NEW | Screen.NEXT:
                compare = dict(_COMPARES)[self.compare]
                if self.screen == Screen.NEW:
                    value = _TEXTS['search_value'].format(value=_TEXTS['unknown'] if self.unknown else self.value)
                else:
                    value = _TEXTS['value'].format(value=self.value)
                texts = {
                    'size': _TEXTS['size'].format(bits=8 * self.width),
                    'compare': _TEXTS['compare'].format(compare=compare),
                    'value': value,
                    'go': _TEXTS['go'],
                }
                title = _TEXTS['new_title'] if self.screen == Screen.NEW else _TEXTS['next_title']
                return title, _TEXTS['form_hint'], View.LIST, rows([texts[e] for e in self._form_entries()])
            case Screen.NUMBER:
                width = self._number_width()
                title = _TEXTS['number_title'].format(bits=8 * width, maximum=(1 << (8 * width)) - 1)
                return (
                    title,
                    _TEXTS['number_hint'],
                    View.NUMBER,
                    [(str(d), i == self.digit) for i, d in enumerate(self.digits)],
                )
            case Screen.RESULTS:
                texts = [
                    _TEXTS['result'].format(address=_hex(r['address']), value=r['value'], previous=r['previous'])
                    if r['value'] is not None
                    else _TEXTS['result_gone'].format(address=_hex(r['address']))
                    for r in self.results
                ]
                title = _TEXTS['results_title'].format(position=cursor + 1, count=len(self.results))
                return title, _TEXTS['results_hint'], View.LIST, rows(texts)
            case Screen.CODES:
                texts = []
                for entry in self._code_entries():
                    if entry == 'restore':
                        count = sum(1 for code in self.codes if code.get('wasFrozen'))
                        texts.append(_TEXTS['restore'].format(count=count))
                        continue
                    code = self.codes[int(entry.removeprefix('code'))]
                    frozen = (
                        _TEXTS['code_frozen']
                        if code['frozen']
                        else _TEXTS['code_saved']
                        if code.get('wasFrozen')
                        else ''
                    )
                    texts.append(
                        _TEXTS['code'].format(
                            address=_hex(code['address']), bits=8 * code['width'], value=code['value'], frozen=frozen
                        )
                    )
                return _TEXTS['codes_title'], _TEXTS['codes_hint'], View.LIST, rows(texts or [_TEXTS['no_code']])
            case Screen.CODE:
                code = (
                    self.codes[self.code]
                    if self.code < len(self.codes)
                    else {'address': 0, 'value': 0, 'frozen': False}
                )
                texts = [
                    _TEXTS['value'].format(value=code['value']),
                    _TEXTS['freeze'].format(state=_TEXTS['on'] if code['frozen'] else _TEXTS['off']),
                    _TEXTS['remove'],
                ]
                title = _TEXTS['code_title'].format(address=_hex(code['address']))
                return title, _TEXTS['code_hint'], View.LIST, rows(texts)
