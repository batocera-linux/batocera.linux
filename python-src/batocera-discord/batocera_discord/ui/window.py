"""The X11 window hosting the overlay: an override-redirect panel on the right edge of the screen.

Openbox forces normal windows fullscreen on Batocera, so the panel bypasses the window manager; it is
created when shown and destroyed when hidden, so nothing runs on the GPU while it is closed.
"""

from __future__ import annotations

import os
import subprocess
import time
from typing import TYPE_CHECKING, Final, Protocol

import pygame

from .. import discord_app
from . import theme
from .overlay import PANEL_WIDTH, Controller, Overlay

if TYPE_CHECKING:
    import threading
    from collections.abc import Callable

    from ..pads import Pads

TITLE: Final = 'Batocera Discord'


class Host(Controller, Protocol):
    pads: Pads

    @property
    def authorizing(self) -> bool: ...
    def pointer_actions(self) -> None: ...


class OverlayWindow:
    def __init__(self, host: Host, /) -> None:
        self.host = host
        self.overlay = Overlay(host)
        self.screen: pygame.Surface | None = None
        self.canvas: pygame.Surface | None = None

    def _geometry(self) -> tuple[int, int, int]:
        width, height = discord_app.screen_size()
        panel = min(PANEL_WIDTH, width // 2)
        return width - panel, panel, height

    def _open(self) -> None:
        x, width, height = self._geometry()
        os.environ['SDL_X11_FORCE_OVERRIDE_REDIRECT'] = '1'
        os.environ['SDL_VIDEO_WINDOW_POS'] = f'{x},0'
        pygame.display.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
        pygame.display.set_caption(TITLE)
        self.canvas = pygame.Surface((width, height))
        self.overlay.on_open()
        self._raise()

    def _close(self) -> None:
        theme.clear_caches()
        pygame.display.quit()
        self.screen = self.canvas = None
        discord_app.focus_emulationstation()

    @staticmethod
    def _raise() -> None:
        subprocess.Popen(
            ['xdotool', 'search', '--name', f'^{TITLE}$', 'windowraise'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def run(self, toggle: threading.Event, set_visible: Callable[[bool], None], /) -> None:
        clock = pygame.time.Clock()
        last_raise = 0.0
        actions = self.host.pads.actions
        while True:
            if toggle.is_set():
                toggle.clear()
                if self.screen is None:
                    self._open()
                    set_visible(True)
                else:
                    self._close()
                    set_visible(False)
                while not actions.empty():
                    actions.get_nowait()
            if self.screen is None or self.canvas is None:
                if self.host.authorizing:
                    self.host.pointer_actions()
                time.sleep(1 / 30)
                continue
            pygame.event.pump()
            while not actions.empty():
                self.overlay.act(actions.get_nowait())
            if toggle.is_set():
                continue
            self.overlay.draw(self.canvas)
            self.overlay.present(self.screen, self.canvas)
            pygame.display.flip()
            if time.monotonic() - last_raise > 2:
                self._raise()
                last_raise = time.monotonic()
            clock.tick(30)
