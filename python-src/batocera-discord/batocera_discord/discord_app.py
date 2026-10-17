"""Install, start and show/hide the Discord flatpak, and drive the X pointer for its consent dialog."""

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
from typing import TYPE_CHECKING, Final

from . import paths
from .errors import PROCESS_ERRORS

if TYPE_CHECKING:
    from collections.abc import Callable

_logger: Final = logging.getLogger(__name__)
_PERCENT_RE: Final = re.compile(r'(\d{1,3})%')
# Electron opens a splash window titled exactly "Discord"; the main window is "<page> - Discord"
_SPLASH_TITLE: Final = 'Discord'


def _env() -> dict[str, str]:
    return {**os.environ, 'XDG_RUNTIME_DIR': str(paths.FLATPAK_RUNTIME_DIR), 'DISPLAY': os.environ.get('DISPLAY', ':0')}


def _run(*args: str, timeout: float = 20) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout, env=_env(), check=False)


def installed() -> bool:
    if shutil.which('flatpak') is None:
        return False
    try:
        return _run('flatpak', 'info', '--system', paths.FLATPAK_APP_ID).returncode == 0
    except PROCESS_ERRORS:
        return False


def install(progress: Callable[[int], None], /) -> bool:
    """Install Discord from Flathub, reporting 0-100 progress. Returns True on success."""
    command = ['flatpak', 'install', '--system', '-y', '--noninteractive', 'flathub', paths.FLATPAK_APP_ID]
    _logger.info('installing %s', paths.FLATPAK_APP_ID)
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=_env()) as proc:
        assert proc.stdout is not None
        for line in proc.stdout:
            if match := _PERCENT_RE.search(line):
                progress(min(100, int(match.group(1))))
        ok = proc.wait() == 0
    if ok and shutil.which('batocera-flatpak-update'):
        # same step as the Flatpak system menu: adds the new app to EmulationStation
        subprocess.run(['batocera-flatpak-update'], check=False, capture_output=True, timeout=120)
    return ok


def launch() -> None:
    """Start Discord in the background (minimized); its IPC socket appears once it is logged in."""
    log = paths.LOG_FILE.with_name('discord-client.log')
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open('ab') as out:
        subprocess.Popen(
            ['flatpak', 'run', paths.FLATPAK_APP_ID, '--start-minimized'],
            stdin=subprocess.DEVNULL,
            stdout=out,
            stderr=out,
            env=_env(),
            start_new_session=True,
        )


def _xdotool(*args: str) -> str:
    if shutil.which('xdotool') is None:
        return ''
    try:
        return subprocess.run(['xdotool', *args], capture_output=True, text=True, timeout=5, check=False).stdout
    except PROCESS_ERRORS:
        return ''


def _windows() -> tuple[list[str], list[str]]:
    """(main windows, splash windows) of the Discord client."""
    main: list[str] = []
    splash: list[str] = []
    for wid in _xdotool('search', '--name', 'Discord').split():
        title = _xdotool('getwindowname', wid).strip()
        if title == _SPLASH_TITLE:
            splash.append(wid)
        elif title.endswith(' - Discord'):
            main.append(wid)
    return main, splash


def show_window() -> None:
    main, splash = _windows()
    for wid in splash:
        _xdotool('windowunmap', wid)
    for wid in main:
        _xdotool('windowmap', wid)
        _xdotool('windowraise', wid)
        _xdotool('windowactivate', wid)


def hide_window() -> None:
    main, splash = _windows()
    for wid in main + splash:
        _xdotool('windowunmap', wid)
    focus_emulationstation()


def focus_emulationstation() -> None:
    _xdotool('search', '--class', 'emulationstation', 'windowactivate')


def screen_size() -> tuple[int, int]:
    try:
        width, height = map(int, _xdotool('getdisplaygeometry').split())
    except ValueError:
        return 1920, 1080
    return width, height


# -- pointer control, used while Discord shows its OAuth consent dialog --
def pointer_center() -> None:
    width, height = screen_size()
    _xdotool('mousemove', str(width // 2), str(height // 2))


def pointer_move(dx: int, dy: int, /) -> None:
    _xdotool('mousemove_relative', '--', str(dx), str(dy))


def pointer_click() -> None:
    _xdotool('click', '1')


def pointer_scroll(down: bool, /, steps: int = 3) -> None:
    _xdotool('click', '--repeat', str(steps), '5' if down else '4')
