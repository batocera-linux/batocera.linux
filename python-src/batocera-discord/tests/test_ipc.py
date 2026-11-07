from __future__ import annotations

import json
import shutil
import socket
import struct
import tempfile
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from batocera_discord import ipc

if TYPE_CHECKING:
    from collections.abc import Iterator


def _send(conn: socket.socket, opcode: int, payload: dict[str, Any], /) -> None:
    body = json.dumps(payload).encode()
    conn.sendall(struct.pack('<II', opcode, len(body)) + body)


def _recv(conn: socket.socket, /) -> tuple[int, dict[str, Any]]:
    header = conn.recv(8, socket.MSG_WAITALL)
    opcode, length = struct.unpack('<II', header)
    return opcode, json.loads(conn.recv(length, socket.MSG_WAITALL))


class FakeDiscord:
    """A tiny Discord client double: handshake, answers commands, sends one event."""

    def __init__(self, path: Path, /) -> None:
        self.path = path
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(str(path))
        self.server.listen(1)
        self.handshake: dict[str, Any] = {}
        self.commands: list[dict[str, Any]] = []
        threading.Thread(target=self._serve, daemon=True).start()

    def _serve(self) -> None:
        conn, _ = self.server.accept()
        with conn:
            _op, self.handshake = _recv(conn)
            _send(conn, ipc.OP_FRAME, {'cmd': 'DISPATCH', 'evt': 'READY', 'data': {'v': 1}})
            while True:
                try:
                    opcode, frame = _recv(conn)
                except OSError, struct.error:
                    return
                if opcode != ipc.OP_FRAME:
                    continue
                self.commands.append(frame)
                if frame['cmd'] == 'FAIL':
                    _send(
                        conn,
                        ipc.OP_FRAME,
                        {'cmd': 'FAIL', 'evt': 'ERROR', 'nonce': frame['nonce'], 'data': {'message': 'nope'}},
                    )
                else:
                    _send(
                        conn,
                        ipc.OP_FRAME,
                        {'cmd': frame['cmd'], 'nonce': frame['nonce'], 'data': {'echo': frame['args']}},
                    )
                    _send(conn, ipc.OP_FRAME, {'cmd': 'DISPATCH', 'evt': 'SPEAKING_START', 'data': {'user_id': '42'}})


@pytest.fixture
def runtime_dir() -> Iterator[Path]:
    # unix socket paths are limited to ~100 characters: keep them short
    directory = Path(tempfile.mkdtemp(prefix='bd', dir='/tmp'))
    yield directory
    shutil.rmtree(directory, ignore_errors=True)


def test_find_socket_prefers_flatpak_path(runtime_dir: Path) -> None:
    flatpak_dir = runtime_dir / 'app' / 'com.discordapp.Discord'
    flatpak_dir.mkdir(parents=True)
    sock = socket.socket(socket.AF_UNIX)
    sock.bind(str(flatpak_dir / 'discord-ipc-0'))

    assert ipc.find_socket((runtime_dir,)) == flatpak_dir / 'discord-ipc-0'
    sock.close()


def test_no_socket(runtime_dir: Path) -> None:
    assert ipc.find_socket((runtime_dir,)) is None


def test_call_and_events(runtime_dir: Path) -> None:
    fake = FakeDiscord(runtime_dir / 'discord-ipc-0')
    events: list[tuple[str, dict[str, Any]]] = []
    received = threading.Event()

    def on_event(evt: str, data: dict[str, Any]) -> None:
        events.append((evt, data))
        received.set()

    client = ipc.DiscordIPC(on_event)
    client.connect('123456789012345678', fake.path)
    answer = client.call('GET_GUILDS', {'x': 1})

    assert fake.handshake == {'v': 1, 'client_id': '123456789012345678'}
    assert answer == {'echo': {'x': 1}}
    assert received.wait(2)
    assert events[0] == ('SPEAKING_START', {'user_id': '42'})

    client.subscribe('VOICE_CHANNEL_SELECT')
    client.subscribe('VOICE_CHANNEL_SELECT')  # already subscribed: not sent twice
    assert [c['cmd'] for c in fake.commands].count('SUBSCRIBE') == 1

    with pytest.raises(ipc.RPCError, match='nope'):
        client.call('FAIL')
    client.close()
    assert not client.connected


def test_call_without_connection() -> None:
    with pytest.raises(ipc.RPCError):
        ipc.DiscordIPC(lambda _evt, _data: None).call('GET_GUILDS')
