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

"""Applies the running emulator's save state spec: migrations, the slot ES asked for, starting from a
state, mirroring serial-named states, and the save/load requests of batocera-savestate.
"""

from __future__ import annotations

import logging
import os
import shutil
import socket
import subprocess
import threading
import zipfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Final

from .client import SOCKET_PATH
from .mirror import StateMirror
from .spec import AUTO, load_spec, render_keys

if TYPE_CHECKING:
    from ..config.config import SystemConfig
    from ..types import HotkeysContext
    from .spec import KeySpec, SaveStateSpec

_logger: Final = logging.getLogger(__name__)

POLL_SECONDS: Final = 1.0
_REQUEST: Final = '/usr/bin/batocera-savestate'

DONE: Final = 0
UNHANDLED: Final = 2
RESTART: Final = 3


def send_hotkey(action: str, /) -> None:
    subprocess.run(
        ['hotkeygen', '--send', action],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        timeout=5,
    )


def _int(value: str | None, /) -> int | None:
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


@dataclass(slots=True)
class SaveStateManager:
    config: SystemConfig
    spec: SaveStateSpec | None
    es_dir: Path | None = field(init=False, default=None)
    romfilename: str = field(init=False, default='')
    # the emulator's own slot for this session, from the one ES asked for
    slot: int | None = field(init=False, default=None)
    boot_args: list[str] = field(init=False, default_factory=list[str])
    # the state ES starts from is in the current slot
    boot_in_slot: bool = field(init=False, default=False)
    mirror: StateMirror | None = field(init=False, default=None)
    _context_keys: frozenset[str] = field(init=False, default=frozenset())
    # the emulator's slots saved to this session
    _saved: set[int] = field(init=False, default_factory=set[int])
    _stop: threading.Event = field(init=False, default_factory=threading.Event)
    _threads: list[threading.Thread] = field(init=False, default_factory=list[threading.Thread])
    _server: socket.socket | None = field(init=False, default=None)
    _server_inode: int | None = field(init=False, default=None)
    _deferred: threading.Timer | None = field(init=False, default=None)

    @property
    def state_file(self) -> Path | None:
        state_file = self.config.get_str('state_filename')
        return Path(state_file) if state_file else None

    def es_path(self, slot: int, /) -> Path | None:
        if self.spec is None or self.es_dir is None or (name := self.spec.es.name(self.romfilename, slot)) is None:
            return None
        return self.es_dir / name

    def prepare(self) -> None:
        if (spec := self.spec) is None:
            return

        self.es_dir = spec.es.directory_path(self.config.system, self.config.emulator, self.config.raw_core)
        self.romfilename = spec.es.romfilename(self.config.rom)
        state_slot = _int(self.config.get_str('state_slot'))
        state_file = self.state_file
        boot_slot = None if state_file is None else spec.es.parse(self.romfilename, state_file.name)

        self._migrate()

        if spec.slots is not None:
            if spec.current_slot:
                # the newest state sits in the current slot, so loading it needs no slot change
                self.slot = boot_slot if boot_slot in spec.slots else self._newest_slot()
            if self.slot is None:
                wanted = spec.es.firstslot if state_slot is None else state_slot
                self.slot = wanted if wanted in spec.slots else self._free_slot(spec.slots)

        if state_file is not None:
            self.boot_args = [arg.format(file=state_file) for arg in spec.boot.args]
            if spec.current_slot and boot_slot == self.slot and state_file.parent == self.es_dir:
                self.boot_in_slot = True
            elif spec.boot.copy and self.slot is not None and (target := self.es_path(self.slot)) is not None:
                try:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(state_file, target)
                    self.boot_in_slot = True
                except OSError:
                    _logger.exception('cannot copy %s to slot %d', state_file, self.slot)

        mirror = spec.mirror
        if mirror is None and spec.slots is not None and (inner := _archive_rom(self.config.rom, spec.archive)):
            native = spec.es.romfilename(inner)
            if native != self.romfilename:
                mirror = spec.es.mirror(self.es_dir, native, spec.slots)

        if mirror is not None:
            self.mirror = StateMirror(
                mirror, spec.es, self.es_dir, self.romfilename, state_slot=state_slot, state_file=state_file
            )
            self.mirror.prepare()

    def _migrate(self) -> None:
        if self.spec is None or self.es_dir is None:
            return

        for migration in self.spec.migrations:
            slots = self.spec.slots if self.spec.slots and '{{slot0}}' in migration.source else (0,)
            for slot in slots:
                source = Path(os.path.normpath(self.es_dir / _render(migration.source, self.romfilename, slot)))
                target = Path(os.path.normpath(self.es_dir / _render(migration.target, self.romfilename, slot)))
                if source == target or not source.is_file() or target.exists():
                    continue

                try:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    source.rename(target)
                    _logger.info('moved state %s to %s', source, target)
                except OSError:
                    _logger.exception('cannot move state %s', source)
                    continue

                # the legacy layout's per-game directory, not one the ES directory sits in
                if not self.es_dir.is_relative_to(source.parent):
                    try:
                        source.parent.rmdir()
                    except OSError:
                        pass

    def _keys(self, name: str, slot: int | None, /) -> KeySpec | None:
        if self.spec is None or (keys := self.spec.keys.get(name)) is None:
            return None
        return render_keys(keys, AUTO if slot is None else slot)

    def hotkeys(self) -> dict[str, KeySpec]:
        """The hotkeygen actions the spec defines; save_state and restore_state go through batocera-savestate."""
        if (spec := self.spec) is None:
            return {}

        keys = spec.keys
        actions: dict[str, KeySpec] = {}

        for name in ('quick_save', 'quick_load', 'save', 'restore', 'save_menu', 'load_menu'):
            if (rendered := self._keys(name, self.slot)) is not None:
                actions[f'savestate_{name}'] = rendered

        for name, action in (('save_slot', 'save_slot'), ('load_slot', 'load_slot'), ('slot', 'slot')):
            if name in keys and spec.slots is not None:
                for slot in spec.slots:
                    if (rendered := self._keys(name, slot)) is not None:
                        actions[f'savestate_{action}_{slot}'] = rendered

        # the pad keeps the emulator's quick slot, otherwise it saves a new state and loads the newest
        if 'quick_save' in keys:
            actions['save_state'] = f'{_REQUEST} save {AUTO}'
        elif keys.keys() & {'save', 'save_slot', 'save_menu'}:
            actions['save_state'] = f'{_REQUEST} save'
        if 'quick_load' in keys:
            actions['restore_state'] = f'{_REQUEST} load {AUTO}'
        elif keys.keys() & {'restore', 'load_slot', 'load_menu'} or spec.boot.args:
            actions['restore_state'] = f'{_REQUEST} load'

        return actions

    def hotkeys_context(self, context: HotkeysContext, /) -> HotkeysContext:
        keys = {**context['keys'], **self.hotkeys()}
        self._context_keys = frozenset(keys)
        return {'name': context['name'], 'keys': keys}

    def _existing_slots(self) -> dict[int, Path]:
        if self.mirror is not None:
            return {slot: path for slot, path in self.mirror.es_states().items() if slot != AUTO}
        if self.spec is None or self.spec.slots is None:
            return {}
        return {slot: path for slot in self.spec.slots if (path := self.es_path(slot)) is not None and path.exists()}

    def _free_slot(self, slots: range, /, *, skip: int | None = None) -> int:
        """The first empty slot, else the oldest state not saved this session."""
        existing = {slot: path for slot, path in self._existing_slots().items() if slot != skip}
        if free := [slot for slot in slots if slot not in existing and slot not in self._saved and slot != skip]:
            return free[0]
        older = {slot: path for slot, path in existing.items() if slot not in self._saved} or existing
        if not older:
            return next(slot for slot in slots if slot != skip)
        return min(older, key=lambda slot: _mtime(older[slot]))

    def _newest_slot(self) -> int | None:
        existing = self._existing_slots()
        return max(existing, key=lambda slot: _mtime(existing[slot])) if existing else None

    def _native_slot(self, es_slot: int, /) -> int | None:
        if self.mirror is not None:
            return self.mirror.native_slot(es_slot)
        return es_slot if self.spec is not None and self.spec.slots is not None and es_slot in self.spec.slots else None

    def _send(self, *actions: str) -> int:
        for action in actions:
            send_hotkey(action)
        return DONE

    def _keep_current_state(self) -> None:
        """Moves the current slot's state to a free slot, so saving there adds a state."""
        if self.spec is None or self.spec.slots is None or self.slot is None:
            return
        if (current := self.es_path(self.slot)) is None or not current.exists():
            return
        if (target := self.es_path(self._free_slot(self.spec.slots, skip=self.slot))) is None:
            return

        try:
            current.replace(target)
            image = current.with_name(f'{current.name}.png')
            if image.exists():
                image.replace(target.with_name(f'{target.name}.png'))
        except OSError:
            _logger.exception('cannot keep the state in %s', current)

    def _save(self) -> int:
        keys = self._context_keys
        spec = self.spec

        if spec is not None and spec.slots is not None:
            if 'savestate_save_menu' in keys:
                slot = self._free_slot(spec.slots)
                self._saved.add(slot)
                return self._send('savestate_save_menu', f'savestate_slot_{slot}')
            if f'savestate_save_slot_{spec.slots.start}' in keys:
                if self.mirror is not None:
                    slot = self.mirror.free_native_slot(spec.slots, self._saved)
                else:
                    slot = self._free_slot(spec.slots)
                self._saved.add(slot)
                return self._send(f'savestate_save_slot_{slot}')
            if spec.current_slot and 'savestate_save' in keys:
                self._keep_current_state()
                return self._send('savestate_save')

        for action in ('savestate_save', 'savestate_quick_save'):
            if action in keys:
                return self._send(action)
        return UNHANDLED

    def _load(self, slot: int | None, /) -> int:
        keys = self._context_keys
        spec = self.spec

        if slot is None and (slot := self._newest_slot()) is None:
            return self._send('savestate_quick_load') if 'savestate_quick_load' in keys else RESTART

        if slot == AUTO:
            if 'savestate_quick_load' in keys:
                return self._send('savestate_quick_load')
        elif 'savestate_load_menu' in keys:
            if slot in self._existing_slots():
                return self._send('savestate_load_menu', f'savestate_slot_{slot}')
        elif (native := self._native_slot(slot)) is not None and f'savestate_load_slot_{native}' in keys:
            return self._send(f'savestate_load_slot_{native}')
        elif (
            spec is not None
            and 'savestate_restore' in keys
            # the current slot, or the emulator's own newest state
            and ((spec.current_slot and slot == self.slot) or (spec.slots is None and slot == self._newest_slot()))
        ):
            return self._send('savestate_restore')

        if f'load_state_slot_{slot}' in keys:
            return self._send(f'load_state_slot_{slot}')
        return RESTART if spec is not None else UNHANDLED

    def request(self, action: str, slot: int | None = None, /) -> int:
        if action == 'save':
            if slot == AUTO and 'savestate_quick_save' in self._context_keys:
                return self._send('savestate_quick_save')
            return self._save()
        return self._load(slot)

    def _boot_action(self) -> str | None:
        if self.spec is None or (state_file := self.state_file) is None or self.spec.boot.send is None:
            return None

        slot = self.spec.es.parse(self.romfilename, state_file.name)
        if slot == AUTO and 'quick_load' in self.spec.keys:
            return 'savestate_quick_load'
        if self.spec.boot.send == 'restore':
            return 'savestate_restore'
        if slot is not None and (native := self._native_slot(slot)) is not None:
            return f'savestate_load_slot_{native}'
        return None

    def game_started(self) -> None:
        if self.spec is not None and (action := self._boot_action()) is not None:
            self._deferred = threading.Timer(self.spec.boot.delay, send_hotkey, (action,))
            self._deferred.daemon = True
            self._deferred.start()

    def _thread(self, target: object, name: str, /) -> None:
        thread = threading.Thread(target=target, name=name, daemon=True)  # pyright: ignore[reportArgumentType]
        thread.start()
        self._threads.append(thread)

    def _watch(self) -> None:
        while self.mirror is not None and not self._stop.wait(POLL_SECONDS):
            self._sync()

    def _sync(self, *, final: bool = False) -> None:
        if self.mirror is None:
            return
        try:
            self.mirror.sync(final=final)
        except Exception:
            _logger.exception('cannot mirror the states of %s', self.romfilename)

    def _serve(self) -> None:
        server = self._server
        while server is not None and not self._stop.is_set():
            try:
                connection, _ = server.accept()
            except OSError:
                return

            with connection:
                try:
                    connection.settimeout(2)
                    words = connection.recv(256).decode().split()
                    code = self.request(words[0], _int(words[1]) if len(words) > 1 else None) if words else UNHANDLED
                except Exception:
                    _logger.exception('save state request failed')
                    code = UNHANDLED

                try:
                    connection.sendall(f'{code}\n'.encode())
                except OSError:
                    pass

    def start(self) -> None:
        if self.mirror is not None:
            self._thread(self._watch, 'savestates-mirror')

        try:
            SOCKET_PATH.parent.mkdir(parents=True, exist_ok=True)
            SOCKET_PATH.unlink(missing_ok=True)
            self._server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._server.bind(str(SOCKET_PATH))
            self._server.listen(4)
            self._server_inode = SOCKET_PATH.stat().st_ino
        except OSError:
            _logger.exception('cannot listen on %s', SOCKET_PATH)
            self._server = None
            return

        self._thread(self._serve, 'savestates-requests')

    def stop(self) -> None:
        self._stop.set()

        if self._deferred is not None:
            self._deferred.cancel()

        if self._server is not None:
            # wakes the accept
            self._server.shutdown(socket.SHUT_RDWR)
            self._server.close()
            # a later launch may have taken the path over, e.g. after ES was killed mid-game
            if _inode(SOCKET_PATH) == self._server_inode:
                SOCKET_PATH.unlink(missing_ok=True)

        for thread in self._threads:
            thread.join(timeout=5)

        if self.mirror is not None:
            self._sync(final=True)
            try:
                self.mirror.write_record()
            except OSError:
                _logger.exception('cannot record the states of %s', self.romfilename)


def _inode(path: Path, /) -> int | None:
    try:
        return path.stat().st_ino
    except OSError:
        return None


def _mtime(path: Path, /) -> int:
    try:
        return path.stat().st_mtime_ns
    except OSError:
        return 0


def _archive_rom(rom: Path, extensions: tuple[str, ...], /) -> Path | None:
    """The one rom inside an archive, which some emulators name states after."""
    if not extensions or rom.suffix.lower() not in ('.zip', '.7z'):
        return None

    try:
        if rom.suffix.lower() == '.zip':
            with zipfile.ZipFile(rom) as archive:
                names = archive.namelist()
        else:
            listing = subprocess.run(
                ['/usr/bin/7z', 'l', '-ba', '-slt', rom], capture_output=True, text=True, check=True, timeout=10
            ).stdout
            names = [line[len('Path = ') :] for line in listing.splitlines() if line.startswith('Path = ')]
    except OSError, zipfile.BadZipFile, subprocess.SubprocessError:
        return None

    roms = [name for name in names if name.rsplit('.', 1)[-1].lower() in extensions]
    return Path(PurePosixPath(roms[0]).name) if len(roms) == 1 else None


def _render(template: str, romfilename: str, slot: int, /) -> str:
    return template.replace('{{romfilename}}', romfilename).replace('{{slot0}}', str(slot))


_managers_lock: Final = threading.Lock()
_managers: Final[dict[int, SaveStateManager]] = {}


def state_manager(config: SystemConfig, /) -> SaveStateManager:
    """The game's manager, prepared by whichever of the plugin and the launcher asks first."""
    with _managers_lock:
        if (manager := _managers.get(id(config))) is None or manager.config is not config:
            manager = _managers[id(config)] = SaveStateManager(config, load_spec(config.emulator))
            try:
                manager.prepare()
            except Exception:
                _logger.exception('cannot prepare the save states of %s', config.rom)

        return manager


def release_state_manager(config: SystemConfig, /) -> SaveStateManager | None:
    with _managers_lock:
        return _managers.pop(id(config), None)
