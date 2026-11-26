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

"""Mirror the states of emulators that name them by game serial into the ES directory.

The ES directory holds the states. At launch the emulator's own folder is rebuilt from it, so a
state deleted or renumbered in ES follows, and while the game runs every state it writes is
linked back.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final

from .screenshots import SCREENSHOTS
from .spec import AUTO

if TYPE_CHECKING:
    from collections.abc import Collection

    from .spec import EsNaming, MirrorSpec

_logger: Final = logging.getLogger(__name__)

type _Key = tuple[int, int, int]


def _key(path: Path, /) -> _Key | None:
    try:
        stat = path.stat()
    except OSError:
        return None

    return stat.st_ino, stat.st_mtime_ns, stat.st_size


def _inode(path: Path, /) -> tuple[int, int] | None:
    try:
        stat = path.stat()
    except OSError:
        return None

    return stat.st_dev, stat.st_ino


def _mtime(path: Path, /) -> int:
    try:
        return path.stat().st_mtime_ns
    except OSError:
        return 0


def link_or_copy(source: Path, target: Path, /) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f'.{target.name}.tmp')
    temporary.unlink(missing_ok=True)

    try:
        os.link(source, temporary)
    except OSError:
        # no hard links on exFAT/NTFS userdata
        shutil.copy2(source, temporary)

    temporary.replace(target)


def write_atomic(target: Path, data: bytes, /) -> None:
    temporary = target.with_name(f'.{target.name}.tmp')
    temporary.write_bytes(data)
    temporary.replace(target)


@dataclass(slots=True)
class StateMirror:
    spec: MirrorSpec
    naming: EsNaming
    es_dir: Path
    romfilename: str
    state_slot: int | None = None
    state_file: Path | None = None
    # every serial the game saved under, a disc swap adds one, the latest last
    serials: list[str] = field(init=False, default_factory=list[str])
    # ES slot -> native slot, for the states placed in the emulator's folder
    live_slots: dict[int, int] = field(init=False, default_factory=dict[int, int])
    _es_slots: dict[Path, int] = field(init=False, default_factory=dict[Path, int])
    _seen: dict[Path, _Key | None] = field(init=False, default_factory=dict[Path, _Key | None])
    _pending: dict[Path, _Key] = field(init=False, default_factory=dict[Path, _Key])

    @property
    def record_path(self) -> Path:
        return self.es_dir / f'.{self.romfilename}.json'

    def es_path(self, slot: int, /) -> Path | None:
        name = self.naming.name(self.romfilename, slot)
        return None if name is None else self.es_dir / name

    def es_states(self) -> dict[int, Path]:
        try:
            paths = list(self.es_dir.iterdir())
        except OSError:
            return {}

        return {slot: path for path in paths if (slot := self.naming.parse(self.romfilename, path.name)) is not None}

    def native_states(self, serials: Collection[str] | None = None, /) -> dict[Path, tuple[str, int]]:
        states: dict[Path, tuple[str, int]] = {}

        for path in self.spec.native_dir.glob(self.spec.glob):
            parsed = self.spec.parse(path.relative_to(self.spec.native_dir).as_posix())
            if parsed is not None and (serials is None or parsed[0] in serials):
                states[path] = parsed

        return states

    def native_slot(self, es_slot: int, /) -> int | None:
        """The game's slot holding the ES state, in the emulator's numbering."""
        for path, slot in self._es_slots.items():
            if slot == es_slot and path.exists() and (parsed := self.spec.parse(self._relative(path))) is not None:
                return parsed[1]
        return None

    def free_native_slot(self, slots: range, saved: Collection[int], /) -> int:
        """The first slot holding none of the game's states, else the oldest one this session left alone."""
        if not self.serials:
            # until the game saves once its serial is unknown, so keep clear of every game's states
            games = Counter(slot for _, slot in self.native_states().values())
            return min((slot for slot in slots if slot not in saved), key=lambda slot: games[slot], default=slots.start)

        states = {slot: path for path, (_, slot) in self.native_states(self.serials[-1:]).items()}
        used = set(states) | set(saved)
        if free := [slot for slot in slots if slot not in used]:
            return free[0]
        older = [slot for slot in slots if slot not in saved and slot in states] or list(slots)
        return min(older, key=lambda slot: _mtime(states[slot]) if slot in states else 0)

    def _relative(self, path: Path, /) -> str:
        return path.relative_to(self.spec.native_dir).as_posix()

    def prepare(self) -> None:
        # emulators fail to save into a folder that doesn't exist
        self.spec.native_dir.mkdir(parents=True, exist_ok=True)

        try:
            record = json.loads(self.record_path.read_text())
            self.serials = [str(serial) for serial in record['serials']]
            placed = {str(name): int(mtime) for name, mtime in record['native'].items()}
        except OSError, ValueError, KeyError, TypeError, AttributeError:
            self.serials = []
            placed = {}

        if self.serials:
            try:
                self._rebuild(placed)
            except Exception:
                _logger.exception('cannot rebuild the states of %s', self.romfilename)

        self._seen = {path: _key(path) for path in self.native_states()}

    def _rebuild(self, placed: dict[str, int], /) -> None:
        es = self.es_states()
        linked = {inode for path in es.values() if (inode := _inode(path)) is not None}

        for path, (_, slot) in sorted(self.native_states(self.serials).items()):
            try:
                stat = path.stat()
            except OSError:
                continue

            relative = path.relative_to(self.spec.native_dir).as_posix()

            # only what ES holds, or what the last session placed and ES has since deleted, goes
            if (
                (stat.st_dev, stat.st_ino) not in linked
                and stat.st_nlink == 1
                and placed.get(relative) != stat.st_mtime_ns
            ):
                es_slot = AUTO if slot == AUTO else self._next_slot(es)
                if not self._store(path, es_slot):
                    continue
                es[es_slot] = path

            path.unlink(missing_ok=True)

        es = self.es_states()
        serial = self.serials[-1]

        if AUTO in es and (name := self.spec.native_name(serial, AUTO)) is not None:
            target = self.spec.native_dir / name
            link_or_copy(es[AUTO], target)
            self._es_slots[target] = AUTO

        slots = sorted(
            (slot for slot in es if slot != AUTO), key=lambda slot: (es[slot] != self.state_file, -_mtime(es[slot]))
        )
        chosen = sorted(slots[: len(self.spec.placement)])

        for native_slot, es_slot in zip(self.spec.placement, chosen, strict=False):
            if (name := self.spec.native_name(serial, native_slot)) is None:
                continue

            target = self.spec.native_dir / name
            link_or_copy(es[es_slot], target)
            self._es_slots[target] = es_slot
            self.live_slots[es_slot] = native_slot

    def _next_slot(self, es: Collection[int], /) -> int:
        taken = set(es) | set(self._es_slots.values())
        return max((slot for slot in taken if slot >= 0), default=self.naming.firstslot - 1) + 1

    def sync(self, *, final: bool = False) -> None:
        states = sorted(self.native_states().items(), key=lambda item: item[1])

        # nothing but the running game writes states, so a change names its serial
        for path, (serial, _) in states:
            if serial not in self.serials and self._seen.get(path) != _key(path):
                self.serials.append(serial)
                for other, (other_serial, _) in states:
                    if other_serial == serial:
                        self._seen.pop(other, None)

        for path, (serial, slot) in states:
            key = _key(path)
            if serial not in self.serials or key is None or self._seen.get(path) == key:
                continue

            if not final and self._pending.get(path) != key:
                # wait for the file to settle, a copy would otherwise catch it half written
                self._pending[path] = key
                continue

            self._pending.pop(path, None)
            self._seen[path] = key
            self.serials.remove(serial)
            self.serials.append(serial)
            self._mirror(path, slot)

    def _mirror(self, path: Path, slot: int, /) -> None:
        es_slot = self._es_slots.get(path)

        if es_slot is None:
            es = self.es_states()
            inode = _inode(path)
            es_slot = next((es_slot for es_slot, es_path in es.items() if _inode(es_path) == inode), None)

            if es_slot is None:
                if slot == AUTO:
                    es_slot = AUTO
                elif (
                    slot == self.spec.fresh
                    and self.state_slot is not None
                    and self.state_slot >= self.naming.firstslot
                    and self.state_slot not in es
                    and self.state_slot not in self._es_slots.values()
                ):
                    # the slot ES picked for a new state
                    es_slot = self.state_slot
                    self.state_slot = None
                elif slot >= self.naming.firstslot and slot not in es and slot not in self._es_slots.values():
                    es_slot = slot
                else:
                    es_slot = self._next_slot(es)

        if self._store(path, es_slot):
            self._es_slots[path] = es_slot

    def _store(self, path: Path, es_slot: int, /) -> bool:
        if (target := self.es_path(es_slot)) is None:
            return False

        if _inode(target) != _inode(path):
            link_or_copy(path, target)

        if (screenshot := SCREENSHOTS.get(self.spec.screenshot or '')) is None:
            return True

        image = target.with_name(f'{target.name}.png')

        try:
            data = screenshot(path)
        except Exception:
            _logger.exception('cannot read the screenshot of %s', path)
            data = None

        if data is None:
            image.unlink(missing_ok=True)
        else:
            write_atomic(image, data)

        return True

    def write_record(self) -> None:
        if not self.serials:
            return

        # only the states this mirror placed or linked to ES, so a later launch never drops one ES lacks
        native = {
            path.relative_to(self.spec.native_dir).as_posix(): _mtime(path)
            for path in self.native_states(self.serials)
            if path in self._es_slots and _key(path) == self._seen.get(path)
        }
        self.es_dir.mkdir(parents=True, exist_ok=True)
        write_atomic(self.record_path, json.dumps({'serials': self.serials, 'native': native}).encode())
