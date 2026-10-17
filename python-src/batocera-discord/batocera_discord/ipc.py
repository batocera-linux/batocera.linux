"""Minimal client for the local Discord RPC over its IPC unix socket.

Frames are ``<opcode:uint32 LE><length:uint32 LE><json>``. Commands carry a nonce and are answered
with the same nonce; events arrive as ``DISPATCH`` frames.
See https://docs.discord.food/topics/rpc
"""

from __future__ import annotations

import json
import logging
import os
import socket
import struct
import threading
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Final, cast

from . import paths

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from pathlib import Path

_logger: Final = logging.getLogger(__name__)

OP_HANDSHAKE: Final = 0
OP_FRAME: Final = 1
OP_CLOSE: Final = 2
OP_PING: Final = 3
OP_PONG: Final = 4

_HEADER: Final = struct.Struct('<II')
_READ_ERRORS: Final = (OSError, ValueError, struct.error)

type EventHandler = Callable[[str, dict[str, Any]], None]


class RPCError(Exception):
    pass


def socket_candidates(runtime_dirs: tuple[Path, ...] | None = None, /) -> Iterator[Path]:
    """Every place a (flatpak or native) Discord client may create its ``discord-ipc-N`` socket."""
    if runtime_dirs is None:
        uid_dir = paths.RUN_DIR / 'user' / str(os.getuid())
        runtime_dirs = (paths.FLATPAK_RUNTIME_DIR, uid_dir, paths.RUN_DIR / 'user' / '1000')
    for index in range(10):
        for base in runtime_dirs:
            yield base / 'app' / paths.FLATPAK_APP_ID / f'discord-ipc-{index}'
            yield base / f'discord-ipc-{index}'


def find_socket(runtime_dirs: tuple[Path, ...] | None = None, /) -> Path | None:
    return next((path for path in socket_candidates(runtime_dirs) if path.is_socket()), None)


@dataclass(slots=True)
class _Pending:
    event: threading.Event = field(default_factory=threading.Event)
    data: dict[str, Any] = field(default_factory=dict[str, Any])
    error: str | None = None


class DiscordIPC:
    def __init__(self, on_event: EventHandler, /) -> None:
        self._on_event = on_event
        self._sock: socket.socket | None = None
        self._pending: dict[str, _Pending] = {}
        self._write_lock = threading.Lock()
        self._subscriptions: set[tuple[str, str]] = set()
        self.ready: dict[str, Any] = {}

    @property
    def connected(self) -> bool:
        return self._sock is not None

    def connect(self, client_id: str, path: Path, /) -> None:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.connect(str(path))
        except OSError as exc:
            sock.close()
            raise RPCError(f'cannot connect to {path}: {exc}') from exc
        self._sock = sock
        self._send(OP_HANDSHAKE, {'v': 1, 'client_id': client_id})
        opcode, data = self._recv()
        if opcode != OP_FRAME or data.get('evt') != 'READY':
            self.close()
            raise RPCError(f'handshake refused: {data.get("message", data)}')
        self.ready = cast('dict[str, Any]', data.get('data') or {})
        threading.Thread(target=self._reader, name='discord-ipc', daemon=True).start()

    def close(self) -> None:
        sock, self._sock = self._sock, None
        if sock is not None:
            try:
                sock.close()
            except OSError:
                pass
        self._subscriptions.clear()
        for pending in self._pending.values():
            pending.error = 'disconnected'
            pending.event.set()
        self._pending.clear()

    def call(
        self, cmd: str, args: dict[str, Any] | None = None, /, *, evt: str | None = None, timeout: float = 10
    ) -> dict[str, Any]:
        if self._sock is None:
            raise RPCError('not connected to Discord')
        nonce = str(uuid.uuid4())
        pending = self._pending[nonce] = _Pending()
        payload: dict[str, Any] = {'cmd': cmd, 'args': args or {}, 'nonce': nonce}
        if evt is not None:
            payload['evt'] = evt
        self._send(OP_FRAME, payload)
        if not pending.event.wait(timeout):
            self._pending.pop(nonce, None)
            raise RPCError(f'{cmd}: no answer from Discord')
        if pending.error is not None:
            raise RPCError(f'{cmd}: {pending.error}')
        return pending.data

    def subscribe(self, evt: str, args: dict[str, Any] | None = None, /) -> None:
        key = (evt, json.dumps(args or {}, sort_keys=True))
        if key not in self._subscriptions:
            self.call('SUBSCRIBE', args, evt=evt)
            self._subscriptions.add(key)

    def unsubscribe(self, evt: str, args: dict[str, Any] | None = None, /) -> None:
        key = (evt, json.dumps(args or {}, sort_keys=True))
        if key in self._subscriptions:
            self._subscriptions.discard(key)
            try:
                self.call('UNSUBSCRIBE', args, evt=evt)
            except RPCError:
                _logger.debug('unsubscribe %s failed', evt)

    # -- framing --
    def _send(self, opcode: int, payload: dict[str, Any], /) -> None:
        if self._sock is None:
            raise RPCError('not connected to Discord')
        body = json.dumps(payload).encode()
        with self._write_lock:
            self._sock.sendall(_HEADER.pack(opcode, len(body)) + body)

    def _recv_exact(self, size: int, /) -> bytes:
        if self._sock is None:
            raise ConnectionError('socket closed')
        buf = bytearray()
        while len(buf) < size:
            chunk = self._sock.recv(size - len(buf))
            if not chunk:
                raise ConnectionError('socket closed')
            buf += chunk
        return bytes(buf)

    def _recv(self) -> tuple[int, dict[str, Any]]:
        opcode, length = _HEADER.unpack(self._recv_exact(_HEADER.size))
        data = json.loads(self._recv_exact(length) or b'{}')
        return opcode, cast('dict[str, Any]', data) if isinstance(data, dict) else {}

    def _reader(self) -> None:
        try:
            while self._sock is not None:
                opcode, data = self._recv()
                if opcode == OP_PING:
                    self._send(OP_PONG, data)
                elif opcode == OP_CLOSE:
                    raise ConnectionError(data.get('message', 'closed by Discord'))
                else:
                    self._dispatch(data)
        except _READ_ERRORS as exc:
            if self._sock is not None:
                _logger.info('Discord IPC closed: %s', exc)
        self.close()

    def _dispatch(self, data: dict[str, Any], /) -> None:
        nonce = data.get('nonce')
        if isinstance(nonce, str) and (pending := self._pending.pop(nonce, None)) is not None:
            payload = cast('dict[str, Any]', data.get('data') or {})
            if data.get('evt') == 'ERROR':
                pending.error = str(payload.get('message', 'error'))
            pending.data = payload
            pending.event.set()
        elif data.get('cmd') == 'DISPATCH':
            try:
                self._on_event(str(data.get('evt')), cast('dict[str, Any]', data.get('data') or {}))
            except Exception:
                _logger.exception('error while handling %s', data.get('evt'))
