from __future__ import annotations

import threading
import time
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest

from batocera_discord import discord_app, session as session_module
from batocera_discord.session import AUTO_INSTALL_DELAYS, MAX_SILENT_LAUNCHES, Session
from batocera_discord.state import Phase, State
from batocera_discord.storage import AppConfig

if TYPE_CHECKING:
    from collections.abc import Callable


class Hooks:
    def authorize_started(self) -> None: ...
    def authorize_finished(self) -> None: ...
    def image_wanted(self, key: str, url: str, /) -> None: ...


class FakeFlatpak:
    """Stands in for the flatpak command: ``release`` lets a pending install finish."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch, *, available: bool = True, result: bool = True) -> None:
        self.available = available
        self.result = result
        self.is_installed = False
        self.installs = 0
        self.release = threading.Event()
        self.release.set()
        self.started = threading.Event()
        monkeypatch.setattr(discord_app, 'flatpak_available', lambda: self.available)
        monkeypatch.setattr(discord_app, 'installed', lambda: self.is_installed)
        monkeypatch.setattr(discord_app, 'install', self.install)

    def install(self, progress: Callable[[int], None], /) -> str:
        self.installs += 1
        self.started.set()
        progress(42)
        self.release.wait(5)
        self.is_installed = self.result
        return '' if self.result else 'Could not resolve hostname dl.flathub.org'


class Clock:
    """Replaces the session's clock only, not the one of the threads."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.now = 1000.0
        monkeypatch.setattr(session_module, 'time', SimpleNamespace(monotonic=lambda: self.now, time=time.time))


def _session(auto_install: bool = True) -> tuple[Session, State]:
    state = State()
    session = Session(state, Hooks(), auto_install=auto_install)
    session._reconfigured.wait = lambda timeout=None: False  # the loop pauses would only slow the tests
    return session, state


def _join(session: Session) -> None:
    assert session._install_thread is not None
    session._install_thread.join(5)


def test_service_start_installs_discord_in_the_background(monkeypatch: pytest.MonkeyPatch) -> None:
    flatpak = FakeFlatpak(monkeypatch)
    flatpak.release.clear()
    session, state = _session()

    session._connect_and_serve()

    assert flatpak.started.wait(5)
    assert state.phase is Phase.INSTALLING
    assert state.install_progress == 42
    flatpak.release.set()
    _join(session)
    assert flatpak.installs == 1
    assert state.phase is Phase.STARTING


def test_install_progress_is_not_hidden_by_the_connection_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    flatpak = FakeFlatpak(monkeypatch)
    flatpak.release.clear()
    AppConfig(client_id='123456789012345678').save()
    session, state = _session(auto_install=False)

    session.install()
    assert flatpak.started.wait(5)
    session.install()  # a second press while installing does nothing
    session._connect_and_serve()  # would otherwise show "not installed" or the setup QR code

    assert state.phase is Phase.INSTALLING
    flatpak.release.set()
    _join(session)
    assert flatpak.installs == 1


def test_no_auto_install_when_disabled_installed_or_without_flatpak(monkeypatch: pytest.MonkeyPatch) -> None:
    flatpak = FakeFlatpak(monkeypatch)
    _session(auto_install=False)[0]._auto_install()

    flatpak.is_installed = True
    _session()[0]._auto_install()

    flatpak.is_installed, flatpak.available = False, False
    _session()[0]._auto_install()

    assert flatpak.installs == 0


def test_failed_auto_install_shows_the_error_then_retries_later(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = Clock(monkeypatch)
    flatpak = FakeFlatpak(monkeypatch, result=False)
    session, state = _session()

    session._connect_and_serve()
    _join(session)
    assert state.phase is Phase.ERROR
    assert state.error == 'Discord install failed: Could not resolve hostname dl.flathub.org'
    session._connect_and_serve()  # the error stays on screen for a while
    assert state.phase is Phase.ERROR

    clock.now += AUTO_INSTALL_DELAYS[0] - 1
    session._connect_and_serve()
    assert flatpak.installs == 1
    assert state.phase is Phase.NO_CONFIG  # the panel offers the setup again meanwhile

    clock.now += 1
    flatpak.result = True
    session._connect_and_serve()
    _join(session)
    assert flatpak.installs == 2
    assert session._discord_installed
    assert state.phase is not Phase.ERROR


def test_auto_install_retries_less_and_less_often(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = Clock(monkeypatch)
    flatpak = FakeFlatpak(monkeypatch, result=False)
    session, _state = _session()

    for delay in (*AUTO_INSTALL_DELAYS, AUTO_INSTALL_DELAYS[-1]):
        session._auto_install()
        _join(session)
        attempts = flatpak.installs
        clock.now += delay - 1
        session._auto_install()
        assert flatpak.installs == attempts
        clock.now += 1

    assert flatpak.installs == len(AUTO_INSTALL_DELAYS) + 1


def _configured_session(monkeypatch: pytest.MonkeyPatch, launch: Callable[[], str], /) -> tuple[Session, State, Clock]:
    clock = Clock(monkeypatch)
    flatpak = FakeFlatpak(monkeypatch)
    flatpak.is_installed = True
    monkeypatch.setattr(discord_app, 'launch', launch)
    monkeypatch.setattr(session_module.ipc, 'find_socket', lambda: None)
    AppConfig(client_id='123456789012345678').save()
    session, state = _session(auto_install=False)
    return session, state, clock


def test_launch_error_is_shown(monkeypatch: pytest.MonkeyPatch) -> None:
    session, state, _clock = _configured_session(monkeypatch, lambda: 'no batocera user to run Discord')

    session._connect_and_serve()

    assert state.phase is Phase.ERROR
    assert state.error == 'Discord cannot start: no batocera user to run Discord'


def test_discord_that_keeps_closing_is_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    launches: list[int] = []

    def launch() -> str:
        launches.append(1)
        return ''

    session, state, clock = _configured_session(monkeypatch, launch)

    for _ in range(MAX_SILENT_LAUNCHES):
        session._connect_and_serve()
        assert state.phase is Phase.LAUNCHING
        clock.now += session_module.LAUNCH_RETRY + 1
    session._connect_and_serve()

    assert len(launches) == MAX_SILENT_LAUNCHES + 1
    assert state.phase is Phase.ERROR
    assert 'discord-client.log' in state.error


def test_discord_still_starting_is_not_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    session, state, clock = _configured_session(monkeypatch, lambda: '')
    session._connect_and_serve()  # launches Discord
    sockets: list[Path] = [Path('/run/user/1000/app/com.discordapp.Discord/discord-ipc-0')]
    monkeypatch.setattr(session_module.ipc, 'find_socket', lambda: sockets[0])

    def refuse(_client_id: str, _path: Path, /) -> None:
        raise ConnectionError('socket closed')

    monkeypatch.setattr(session.rpc, 'connect', refuse)

    session._connect_and_serve()
    assert state.phase is Phase.LAUNCHING

    clock.now += session_module.STARTUP_GRACE + 1
    with pytest.raises(ConnectionError):
        session._connect_and_serve()
