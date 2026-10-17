from __future__ import annotations

import grp
import os
import pwd
import shutil
import socket
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

from batocera_discord import discord_app, paths

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    import pytest


class Recorder:
    def __init__(self) -> None:
        self.calls: list[tuple[list[str], dict[str, Any]]] = []
        self.chowned: list[str] = []

    def __call__(self, command: list[str], /, **kwargs: Any) -> None:
        self.calls.append((command, kwargs))


def _which(name: str, /) -> str:
    return f'/usr/bin/{name}'


def _no_chown(_path: Path, _uid: int, _gid: int, /) -> None: ...


def _audio_group(name: str, /) -> grp.struct_group:
    return grp.struct_group((name, 'x', 29, []))


def _fake_box(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, running: bool = False) -> Recorder:
    """A root service on Batocera: Discord must start as the batocera user, in a D-Bus session."""
    popen = Recorder()
    account = pwd.struct_passwd(('batocera', 'x', 1000, 1000, '', '/userdata/system', '/bin/bash'))
    monkeypatch.setattr(paths, 'RUN_DIR', tmp_path / 'run')
    monkeypatch.setattr(paths, 'PULSE_SOCKET', tmp_path / 'run' / 'pulse' / 'native')
    monkeypatch.setattr(paths, 'FLATPAK_HOME', tmp_path / 'flatpak-data')
    monkeypatch.setattr(paths, 'DISCORD_USER_DIR', tmp_path / 'discord-user')
    monkeypatch.setattr(paths, 'LOG_FILE', tmp_path / 'logs' / 'discord.log')
    monkeypatch.setattr(discord_app, 'running', lambda: running)

    def chown(path: Path, _uid: int, _gid: int, /) -> None:
        popen.chowned.append(str(path))

    def getgrouplist(_name: str, gid: int, /) -> list[int]:
        return [gid, 29, 28, 107]  # audio, video, input

    def getpwnam(_name: str, /) -> pwd.struct_passwd:
        return account

    monkeypatch.setattr(shutil, 'which', _which)
    monkeypatch.setattr(os, 'geteuid', lambda: 0)
    monkeypatch.setattr(os, 'chown', chown)
    monkeypatch.setattr(os, 'getgrouplist', getgrouplist)
    monkeypatch.setattr(pwd, 'getpwnam', getpwnam)
    monkeypatch.setattr(subprocess, 'Popen', popen)
    monkeypatch.delenv('DBUS_SESSION_BUS_ADDRESS', raising=False)
    monkeypatch.setenv('DISPLAY', ':0')
    return popen


def test_root_service_starts_discord_as_batocera(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    popen = _fake_box(tmp_path, monkeypatch)

    discord_app.launch()

    [(command, kwargs)] = popen.calls
    assert command[:3] == ['dbus-run-session', '--', 'flatpak']
    assert command[-2:] == [paths.FLATPAK_APP_ID, '--start-minimized']
    assert (kwargs['user'], kwargs['group']) == (1000, 1000)
    assert 29 in kwargs['extra_groups']  # audio
    env = kwargs['env']
    assert env['HOME'] == str(tmp_path / 'flatpak-data')
    assert env['XDG_RUNTIME_DIR'] == str(tmp_path / 'run' / 'user' / '1000')
    assert env['PULSE_SERVER'] == f'unix:{paths.PULSE_SOCKET}'  # no audio server in this fake box
    assert env['USER'] == 'batocera'
    assert env['XDG_CACHE_HOME'] == str(tmp_path / 'discord-user' / '.cache')
    runtime_dir = tmp_path / 'run' / 'user' / '1000'
    data_dir = tmp_path / 'flatpak-data' / '.var' / 'app' / paths.FLATPAK_APP_ID
    assert (runtime_dir.stat().st_mode & 0o777, data_dir.stat().st_mode & 0o777) == (0o700, 0o700)
    assert {str(runtime_dir), str(data_dir), env['XDG_CACHE_HOME'], env['XDG_DATA_HOME']} <= set(popen.chowned)


def test_existing_session_bus_is_reused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    popen = _fake_box(tmp_path, monkeypatch)
    monkeypatch.setattr(os, 'geteuid', lambda: 1000)
    monkeypatch.setenv('DBUS_SESSION_BUS_ADDRESS', 'unix:path=/run/user/1000/bus')

    discord_app.launch()

    [(command, kwargs)] = popen.calls
    assert command[0] == 'flatpak'
    assert kwargs['user'] is None
    assert kwargs['env']['DBUS_SESSION_BUS_ADDRESS'] == os.environ['DBUS_SESSION_BUS_ADDRESS']


def test_no_second_client_while_one_is_logging_in(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    popen = _fake_box(tmp_path, monkeypatch, running=True)

    discord_app.launch()

    assert not popen.calls


def test_no_batocera_user_is_reported(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    popen = _fake_box(tmp_path, monkeypatch)

    def getpwnam(name: str, /) -> pwd.struct_passwd:
        raise KeyError(name)

    monkeypatch.setattr(pwd, 'getpwnam', getpwnam)

    assert discord_app.launch() == 'no batocera user to run Discord'
    assert not popen.calls


@contextmanager
def _audio_server() -> Generator[tuple[Path, socket.socket]]:
    """A listening unix socket standing for /run/pulse/native (short path: unix sockets have a length limit)."""
    base = Path(tempfile.mkdtemp(prefix='bd', dir='/tmp'))
    server = socket.socket(socket.AF_UNIX)
    try:
        (base / 'pulse').mkdir(mode=0o700)
        server.bind(str(base / 'pulse' / 'native'))
        server.listen()
        yield base, server
    finally:
        server.close()
        shutil.rmtree(base)


def _share(base: Path, monkeypatch: pytest.MonkeyPatch, /) -> str:
    monkeypatch.setattr(paths, 'RUN_DIR', base)
    monkeypatch.setattr(paths, 'PULSE_SOCKET', base / 'pulse' / 'native')
    monkeypatch.setattr(os, 'chown', _no_chown)
    account = pwd.struct_passwd(('batocera', 'x', 1000, 1000, '', '/userdata/system', '/bin/bash'))
    return discord_app.share_pulse_socket(account)


def test_audio_socket_is_linked_for_the_discord_user(monkeypatch: pytest.MonkeyPatch) -> None:
    with _audio_server() as (base, server):
        link = base / 'user' / '1000' / 'pulse' / 'native'

        assert _share(base, monkeypatch) == f'unix:{link}'
        assert link.samefile(base / 'pulse' / 'native')
        with socket.socket(socket.AF_UNIX) as client:
            client.connect(str(link))  # reached through the link, whatever the rights of pulse/
        server.accept()[0].close()

        # the audio server restarted: a new socket, the link follows it
        server.close()
        (base / 'pulse' / 'native').unlink()
        with socket.socket(socket.AF_UNIX) as restarted:
            restarted.bind(str(base / 'pulse' / 'native'))
            assert _share(base, monkeypatch) == f'unix:{link}'
            assert link.samefile(base / 'pulse' / 'native')


def test_audio_falls_back_to_group_access(monkeypatch: pytest.MonkeyPatch) -> None:
    def no_link(*_args: object) -> None:
        raise OSError(18, 'Invalid cross-device link')

    with _audio_server() as (base, _server):
        monkeypatch.setattr(os, 'link', no_link)
        monkeypatch.setattr(grp, 'getgrnam', _audio_group)

        assert _share(base, monkeypatch) == f'unix:{base / "pulse" / "native"}'
        assert (base / 'pulse').stat().st_mode & 0o777 == 0o750


def test_install_reports_why_flatpak_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    output = [
        'Looking for matches…',
        '\x1b[1mInstalling…\x1b[0m ████   12%  4.1 MB/s',
        'error: Unable to load summary from remote flathub: Could not resolve hostname',
    ]

    def run(*_args: str, timeout: float = 20) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess([], 0)

    def terminal(_command: list[str], on_line: Callable[[str], None], /) -> int:
        for line in output:
            on_line(line)
        return 1

    progress: list[int] = []
    monkeypatch.setattr(shutil, 'which', _which)
    monkeypatch.setattr(discord_app, '_run', run)
    monkeypatch.setattr(discord_app, 'run_in_terminal', terminal)

    reason = discord_app.install(progress.append)

    assert reason == 'error: Unable to load summary from remote flathub: Could not resolve hostname'
    assert progress == [12]


def test_overall_progress_over_several_refs() -> None:
    progress: list[int] = []
    overall = discord_app.InstallProgress(progress.append)

    for line in (
        'Installing 1/2…  ████        50%  80 MB/s',
        'Installing 1/2…  ████████   100%',
        'Installing 2/2…              0%',  # the second ref starts: the bar must not go back
        'Installing 2/2…  ████        50%',
        'Installing 2/2…  ████████   100%',
        ' 1.     com.discordapp.Discord    stable   i    flathub   < 247.1 MB',
    ):
        overall.feed(line)

    assert progress == [25, 50, 75, 100]


def test_progress_is_read_from_a_terminal() -> None:
    lines: list[str] = []
    script = 'test -t 1 || exit 3; printf "Installing…  10%%\\rInstalling…  60%%\\rdone\\n"'

    assert discord_app.run_in_terminal(['sh', '-c', script], lines.append) == 0
    assert lines == ['Installing…  10%', 'Installing…  60%', 'done']
