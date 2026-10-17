"""The ``discord`` service: ties the Discord session, the pads, the overlay window and the setup page."""

from __future__ import annotations

import fcntl
import logging
import os
import signal
import subprocess
import threading
import time
from logging.handlers import RotatingFileHandler
from typing import IO, TYPE_CHECKING, Final

from . import audio, discord_app, paths
from .controls import Action, Family
from .errors import IO_ERRORS, PROCESS_ERRORS
from .i18n import _
from .images import ImageCache
from .pads import Pads
from .session import Session
from .setup_server import SetupServer
from .state import Phase, State

if TYPE_CHECKING:
    from pathlib import Path

_logger: Final = logging.getLogger(__name__)

FPS: Final = 30
POINTER_SPEED: Final = 14  # pixels per tick at full stick deflection
RAISE_EVERY: Final = 2.0  # seconds: stay above a game that raises its own window


def setting(key: str, /, default: str = '') -> str:
    try:
        value = subprocess.run(
            ['batocera-settings-get', key], capture_output=True, text=True, timeout=5, check=False
        ).stdout.strip()
    except PROCESS_ERRORS:
        value = ''
    return value or default


class App:
    def __init__(self) -> None:
        self.state = State()
        self.images = ImageCache(self.state.bump)
        self.session = Session(self.state, self, auto_install=setting('discord.autoinstall', '1') != '0')
        self.pads = Pads(self.request_toggle, guide_enabled=setting('discord.guidebutton', '1') != '0')
        self.setup = SetupServer(self.state, self.session.reconfigure, self.session.logout)
        self._toggle = threading.Event()
        self._stopping = threading.Event()
        self._visible = False
        self._authorizing = False

    # ------------------------------------------------------- SessionHooks
    def authorize_started(self) -> None:
        """Discord shows its consent dialog: hide the panel and let the stick drive the X pointer."""
        self._authorizing = True
        if self._visible:
            self._toggle.set()
        self.pads.pointer = self._move_pointer
        self.pads.grab(True)
        discord_app.show_window()
        time.sleep(1.5)
        discord_app.pointer_center()
        discord_app.pointer_scroll(True, 12)  # the Authorize button is at the bottom of a scrolling dialog

    def authorize_finished(self) -> None:
        self._authorizing = False
        self.pads.pointer = None
        self.pads.grab(self._visible)
        discord_app.hide_window()

    def image_wanted(self, key: str, url: str, /) -> None:
        self.images.want(key, url)

    @staticmethod
    def _move_pointer(x: float, y: float, /) -> None:
        discord_app.pointer_move(int(x * POINTER_SPEED), int(y * POINTER_SPEED))

    # --------------------------------------------------- overlay Controller
    def family(self) -> Family:
        return self.pads.last_family

    def image_path(self, key: str, /) -> Path:
        return self.images.path(key)

    def setup_url(self) -> str | None:
        return self.setup.url()

    def install_discord(self) -> None:
        self.session.install()

    def show_discord_window(self) -> None:
        self.close_overlay()
        threading.Thread(target=discord_app.show_window, daemon=True).start()

    def close_overlay(self) -> None:
        if self._visible:
            self._toggle.set()

    def load_channels(self, guild_id: str, /) -> None:
        self.session.run_later(lambda: self.session.load_channels(guild_id))

    def join(self, channel_id: str, /) -> None:
        self.session.join(channel_id)

    def leave(self) -> None:
        self.session.leave()

    def toggle_mute(self) -> None:
        self.session.toggle_mute()

    def toggle_deaf(self) -> None:
        self.session.toggle_deaf()

    def set_user_volume(self, user_id: str, volume: int, /) -> None:
        self.session.set_user_volume(user_id, volume)

    def set_user_mute(self, user_id: str, mute: bool, /) -> None:
        self.session.set_user_mute(user_id, mute)

    def logout(self) -> None:
        threading.Thread(target=self.session.logout, daemon=True).start()

    def recents(self) -> list[dict[str, str]]:
        return list(self.session.recents)

    # ----------------------------------------------------------- main loop
    def request_toggle(self) -> None:
        if not self._authorizing:
            self._toggle.set()

    def stop(self) -> None:
        self._stopping.set()
        self.pads.release()
        self.setup.stop()

    def run(self) -> None:
        _.set_language()
        self.images.start()
        self.session.start()
        self.pads.start()
        audio.start_watcher(self.state)
        threading.Thread(
            target=discord_app.keep_pulse_socket, args=(self._stopping,), name='discord-pulse', daemon=True
        ).start()
        # imported late: pygame prints a banner and must see the SDL environment set by main()
        from .ui.window import OverlayWindow

        OverlayWindow(self).run(self._toggle, self._set_visible)

    def _set_visible(self, visible: bool, /) -> None:
        self._visible = visible
        self.pads.grab(visible or self._authorizing)
        if not visible and self.state.phase is Phase.READY:
            self.setup.stop()  # configured: the setup page is no longer needed

    @property
    def authorizing(self) -> bool:
        return self._authorizing

    def pointer_actions(self) -> None:
        """While Discord's consent dialog is shown, buttons click and the right stick scrolls."""
        while not self.pads.actions.empty():
            action = self.pads.actions.get_nowait()
            if action is Action.CONFIRM:
                discord_app.pointer_click()
            elif action in (Action.SCROLL_DOWN, Action.SCROLL_UP):
                discord_app.pointer_scroll(action is Action.SCROLL_DOWN)


def _single_instance() -> IO[str] | None:
    paths.LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    lock = paths.LOCK_FILE.open('w')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        lock.close()
        return None
    return lock


def run_daemon() -> int:
    paths.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(paths.LOG_FILE, maxBytes=256 * 1024, backupCount=1)
    logging.basicConfig(
        level=logging.INFO, handlers=[handler], format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    if (lock := _single_instance()) is None:
        _logger.error('already running')
        return 1
    os.environ.setdefault('DISPLAY', ':0')
    os.environ['SDL_NO_SIGNAL_HANDLERS'] = '1'  # otherwise SDL swallows SIGTERM and the service never stops
    paths.PID_FILE.write_text(str(os.getpid()))
    app = App()

    def stop(*_args: object) -> None:
        app.stop()
        paths.PID_FILE.unlink(missing_ok=True)
        os._exit(0)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    def toggle(*_args: object) -> None:
        app.request_toggle()

    signal.signal(signal.SIGUSR1, toggle)
    _logger.info('started, pid %s (lock %s held)', os.getpid(), lock.name)
    app.run()
    return 0


def send_toggle() -> int:
    try:
        os.kill(int(paths.PID_FILE.read_text()), signal.SIGUSR1)
    except IO_ERRORS:
        return 1
    return 0
