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

"""Save state specs, the `savestates` sections of the emulator YAML files.

The ES part keeps es_savestates.cfg's attribute names; batocera-es-system writes both that file
and the JSON these are loaded from.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, Literal, cast

from batocera_common.paths import SAVES

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

_logger: Final = logging.getLogger(__name__)

SPECS_PATH: Final = Path('/usr/share/batocera/launch/savestates.json')

# ES's slot for the autosave
AUTO: Final = -1

type KeySpec = str | list[str]

_TOKEN: Final = re.compile(r'\{\{(romfilename|slot|slot0|slot00|slot2d)\}\}')


def render_keys(keys: KeySpec, slot: int, /) -> KeySpec:
    if isinstance(keys, str):
        return keys.format(slot=slot)
    return [key.format(slot=slot) for key in keys]


def _slot_text(token: str, slot: int, /) -> str:
    if token == 'slot':
        return '' if slot == 0 else str(slot)
    if token == 'slot0':
        return str(slot)
    return f'{slot:02d}'


def _render(template: str, romfilename: str, slot: int, /) -> str:
    return _TOKEN.sub(lambda match: romfilename if match[1] == 'romfilename' else _slot_text(match[1], slot), template)


@dataclass(frozen=True, slots=True, kw_only=True)
class EsNaming:
    """How ES names a game's states, as es_savestates.cfg describes it."""

    directory: str
    file: str
    autosave_file: str | None = None
    image: str | None = None
    nofileextension: bool = True
    firstslot: int = 0

    def directory_path(self, system: str, emulator: str, core: str | None, /) -> Path:
        path = self.directory.replace('{{system}}', system).replace('{{emulator}}', emulator)
        path = path.replace('{{core}}', core or emulator)
        return Path(path) if path.startswith('/') else SAVES / path

    def romfilename(self, rom: Path, /) -> str:
        return rom.stem if self.nofileextension else rom.name

    def name(self, romfilename: str, slot: int, /) -> str | None:
        template = self.autosave_file if slot == AUTO else self.file
        return _render(template, romfilename, slot) if template else None

    def image_name(self, romfilename: str, slot: int, /) -> str | None:
        return _render(self.image, romfilename, slot) if self.image and slot != AUTO else None

    def parse(self, romfilename: str, name: str, /) -> int | None:
        if self.autosave_file and name == self.name(romfilename, AUTO):
            return AUTO

        if not self.file:
            return None

        parts: list[str] = []
        position = 0
        for match in _TOKEN.finditer(self.file):
            parts.append(re.escape(self.file[position : match.start()]))
            parts.append(re.escape(romfilename) if match[1] == 'romfilename' else '([0-9]*)')
            position = match.end()
        parts.append(re.escape(self.file[position:]))

        if (match := re.fullmatch(''.join(parts), name)) is None:
            return None

        return int(match[1]) if match[1] else 0

    def mirror(self, native_dir: Path, romfilename: str, slots: range, /) -> MirrorSpec:
        """States the emulator names after another rom name, in the same directory."""
        pattern: list[str] = []
        name: list[str] = []
        position = 0
        for match in _TOKEN.finditer(self.file):
            literal = self.file[position : match.start()]
            pattern.append(re.escape(literal))
            name.append(literal.replace('{', '{{').replace('}', '}}'))
            if match[1] == 'romfilename':
                pattern.append(f'(?P<serial>{re.escape(romfilename)})')
                name.append('{serial}')
            else:
                pattern.append('(?P<slot>[0-9]+)')
                name.append('{slot:02d}' if match[1] in ('slot00', 'slot2d') else '{slot}')
            position = match.end()
        pattern.append(re.escape(self.file[position:]))
        name.append(self.file[position:].replace('{', '{{').replace('}', '}}'))

        return MirrorSpec(
            native_dir=native_dir,
            glob='*',
            pattern=re.compile(''.join(pattern)),
            slot_name=''.join(name),
            placement=tuple(slots),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class MirrorSpec:
    """An emulator that names states by game serial; pattern has the groups serial and slot."""

    native_dir: Path
    glob: str
    pattern: re.Pattern[str]
    slot_name: str
    auto_name: str | None = None
    # slots refilled from ES at launch, the most recent states first
    placement: tuple[int, ...] = ()
    # the slot the emulator saves to until told otherwise, left empty for a new state
    fresh: int | None = None
    # the emulator's quick slot, listed by ES as the autosave
    auto_slot: int | None = None
    screenshot: str | None = None

    def parse(self, relative: str, /) -> tuple[str, int] | None:
        if (match := self.pattern.fullmatch(relative)) is None:
            return None

        slot = AUTO if match['slot'] is None else int(match['slot'])
        return match['serial'], AUTO if slot == self.auto_slot else slot

    def native_name(self, serial: str, slot: int, /) -> str | None:
        template = self.slot_name
        if slot == AUTO:
            if self.auto_name is None and self.auto_slot is None:
                return None
            template = self.auto_name or self.slot_name
            slot = AUTO if self.auto_slot is None else self.auto_slot

        return template.format(serial=serial, slot=slot, digits=len(str(slot)))


@dataclass(frozen=True, slots=True)
class Migration:
    """Moves a legacy state to its ES name, in the ES directory, when the target is free."""

    source: str
    target: str


@dataclass(frozen=True, slots=True, kw_only=True)
class BootSpec:
    args: tuple[str, ...] = ()
    # copy the state into the current slot
    copy: bool = False
    # the hotkey that loads it once the game runs
    send: Literal['load', 'restore'] | None = None
    delay: float = 5.0


@dataclass(frozen=True, slots=True, kw_only=True)
class SaveStateSpec:
    es: EsNaming
    slots: range | None = None
    keys: Mapping[str, KeySpec] = field(default_factory=dict[str, KeySpec])
    boot: BootSpec = field(default_factory=BootSpec)
    mirror: MirrorSpec | None = None
    migrations: tuple[Migration, ...] = ()
    # rom extensions the emulator names states after when it opens them from an archive
    archive: tuple[str, ...] = ()

    @property
    def current_slot(self) -> bool:
        """An emulator that saves to and loads its current slot only."""
        keys = self.keys
        return (
            self.slots is not None
            and self.mirror is None
            and 'save' in keys
            and 'save_slot' not in keys
            and 'slot' not in keys
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], /) -> SaveStateSpec:
        slots: Sequence[int] | None = data.get('slots')
        boot: Mapping[str, Any] = data.get('boot', {})
        mirror: Mapping[str, Any] | None = data.get('mirror')

        return cls(
            es=EsNaming(
                directory=data['directory'],
                file=data.get('file', ''),
                autosave_file=data.get('autosave_file') or None,
                image=data.get('image') or None,
                nofileextension=data.get('nofileextension', True),
                firstslot=data.get('firstslot', 0),
            ),
            slots=range(slots[0], slots[1] + 1) if slots else None,
            keys=dict(data.get('keys', {})),
            boot=BootSpec(
                args=tuple(boot.get('args', ())),
                copy=boot.get('copy', False),
                send=boot.get('send'),
                delay=boot.get('delay', 5.0),
            ),
            mirror=MirrorSpec(
                native_dir=Path(mirror['native_dir']),
                glob=mirror['glob'],
                pattern=re.compile(mirror['pattern']),
                slot_name=mirror['slot_name'],
                auto_name=mirror.get('auto_name'),
                placement=tuple(range(mirror['placement'][0], mirror['placement'][1] + 1))
                if 'placement' in mirror
                else (),
                fresh=mirror.get('fresh'),
                auto_slot=mirror.get('auto_slot'),
                screenshot=mirror.get('screenshot'),
            )
            if mirror is not None
            else None,
            migrations=tuple(Migration(item['from'], item['to']) for item in data.get('migrate', ())),
            archive=tuple(data.get('archive', ())),
        )


def load_spec(emulator: str, /, path: Path = SPECS_PATH) -> SaveStateSpec | None:
    try:
        specs = cast('dict[str, Mapping[str, Any]]', json.loads(path.read_text()))
    except FileNotFoundError:
        return None
    except OSError, ValueError:
        _logger.exception('cannot read %s', path)
        return None

    if (data := specs.get(emulator)) is None:
        return None

    try:
        return SaveStateSpec.from_dict(data)
    except KeyError, TypeError, ValueError, re.error:
        _logger.exception('invalid save state spec for %s', emulator)
        return None
