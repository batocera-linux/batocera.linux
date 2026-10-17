from __future__ import annotations

import threading
import time
from types import SimpleNamespace
from typing import TYPE_CHECKING

from batocera_discord import discord_app, session as session_module
from batocera_discord.session import AUTO_INSTALL_RETRY, Session
from batocera_discord.state import Phase, State
from batocera_discord.storage import AppConfig

if TYPE_CHECKING:
    from collections.abc import Callable

    import pytest


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

    def install(self, progress: Callable[[int], None], /) -> bool:
        self.installs += 1
        self.started.set()
        progress(42)
        self.release.wait(5)
        self.is_installed = self.result
        return self.result


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
    session._connect_and_serve()  # the error stays on screen for a while
    assert state.phase is Phase.ERROR

    clock.now += AUTO_INSTALL_RETRY - 1
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
