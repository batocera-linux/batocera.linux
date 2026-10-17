"""Install, start and show/hide the Discord flatpak, and drive the X pointer for its consent dialog."""

from __future__ import annotations

import grp
import logging
import os
import pwd
import re
import resource
import shutil
import subprocess
from collections import deque
from typing import TYPE_CHECKING, Final

from . import paths
from .errors import ACCOUNT_ERRORS, PROCESS_ERRORS

if TYPE_CHECKING:
    import threading
    from collections.abc import Callable
    from pathlib import Path

_logger: Final = logging.getLogger(__name__)
_PERCENT_RE: Final = re.compile(r'(\d{1,3})%')
# Electron opens a splash window titled exactly "Discord"; the main window is "<page> - Discord"
_SPLASH_TITLE: Final = 'Discord'
_OPEN_FILES: Final = 4096  # Electron keeps many files open
_ANSI_RE: Final = re.compile(r'\x1b\[[0-9;?]*[A-Za-z]|\r')
FLATHUB_REPO: Final = 'https://dl.flathub.org/repo/flathub.flatpakrepo'
PULSE_CHECK_EVERY: Final = 5.0  # seconds


def _env() -> dict[str, str]:
    return {**os.environ, 'XDG_RUNTIME_DIR': str(paths.FLATPAK_RUNTIME_DIR), 'DISPLAY': os.environ.get('DISPLAY', ':0')}


def _run(*args: str, timeout: float = 20) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout, env=_env(), check=False)


def flatpak_available() -> bool:
    return shutil.which('flatpak') is not None


def installed() -> bool:
    if not flatpak_available():
        return False
    try:
        return _run('flatpak', 'info', '--system', paths.FLATPAK_APP_ID).returncode == 0
    except PROCESS_ERRORS:
        return False


def install(progress: Callable[[int], None], /) -> str:
    """Install Discord from Flathub, reporting 0-100 progress. Returns '' on success, else the reason."""
    if not flatpak_available():
        return 'flatpak is not available'
    try:
        # Batocera ships the Flathub remote, but it may have been removed: add it back if needed
        _run('flatpak', 'remote-add', '--system', '--if-not-exists', 'flathub', FLATHUB_REPO, timeout=120)
    except PROCESS_ERRORS:
        _logger.warning('cannot check the flathub remote', exc_info=True)
    command = ['flatpak', 'install', '--system', '-y', '--noninteractive', 'flathub', paths.FLATPAK_APP_ID]
    _logger.info('installing %s', paths.FLATPAK_APP_ID)
    last_lines: deque[str] = deque(maxlen=4)
    try:
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=_env()) as proc:
            assert proc.stdout is not None
            for line in proc.stdout:
                if match := _PERCENT_RE.search(line):
                    progress(min(100, int(match.group(1))))
                elif text := _ANSI_RE.sub('', line).strip():
                    last_lines.append(text)
            ok = proc.wait() == 0
    except PROCESS_ERRORS as exc:
        _logger.exception('cannot run flatpak install')
        return str(exc)
    if not ok:
        reason = next((line for line in reversed(last_lines) if 'error' in line.lower()), '') or (
            last_lines[-1] if last_lines else 'flatpak install failed'
        )
        _logger.error('flatpak install failed: %s', ' | '.join(last_lines))
        return reason[:160]
    if shutil.which('batocera-flatpak-update'):
        # same step as the Flatpak system menu: adds the new app to EmulationStation
        try:
            subprocess.run(['batocera-flatpak-update'], check=False, capture_output=True, timeout=120)
        except PROCESS_ERRORS:
            _logger.warning('batocera-flatpak-update failed', exc_info=True)
    return ''


def running() -> bool:
    """A Discord client is already running, maybe still logging in (its IPC socket answers later)."""
    try:
        return _run('pgrep', '-f', f'flatpak run .*{re.escape(paths.FLATPAK_APP_ID)}').returncode == 0
    except PROCESS_ERRORS:
        return False


def _raise_open_files_limit() -> None:
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    wanted = _OPEN_FILES if hard == resource.RLIM_INFINITY else min(_OPEN_FILES, hard)
    if soft != resource.RLIM_INFINITY and soft < wanted:
        resource.setrlimit(resource.RLIMIT_NOFILE, (wanted, hard))


def _owned_dir(path: Path, uid: int, gid: int, /) -> None:
    path.mkdir(parents=True, exist_ok=True)
    os.chown(path, uid, gid)
    path.chmod(0o700)


def _client_account() -> pwd.struct_passwd | None:
    """The user the Discord client runs as, None when the service itself is not root."""
    if os.geteuid() != 0:
        return None
    try:
        return pwd.getpwnam(paths.DISCORD_USER)
    except KeyError:
        return None


def share_pulse_socket(account: pwd.struct_passwd, /) -> str:
    """Let the Discord user reach the audio server; returns the PULSE_SERVER to give it.

    Batocera keeps /run/pulse private to root, and every pulse client run by root resets it to 0700.
    A unix socket is reached through its inode, so the socket is hard linked into the user's own
    runtime directory instead. If that is not possible, the directory is opened to the audio group,
    as the flatpak emulator of Batocera does. Called again regularly by ``keep_pulse_socket``.
    """
    source = paths.PULSE_SOCKET
    if not source.is_socket():
        return f'unix:{source}'
    link = paths.RUN_DIR / 'user' / str(account.pw_uid) / 'pulse' / 'native'
    try:
        _owned_dir(link.parent.parent, account.pw_uid, account.pw_gid)
        _owned_dir(link.parent, account.pw_uid, account.pw_gid)
        if not (link.exists() and link.samefile(source)):
            temporary = link.with_name('native.new')
            temporary.unlink(missing_ok=True)
            os.link(source, temporary)
            temporary.replace(link)
            _logger.info('audio server shared with %s through %s', account.pw_name, link)
    except OSError as exc:
        _logger.warning('cannot link the audio socket (%s): opening %s to the audio group', exc, source.parent)
        try:
            os.chown(source.parent, 0, grp.getgrnam('audio').gr_gid)
            source.parent.chmod(0o750)
        except ACCOUNT_ERRORS:
            _logger.exception('cannot share the audio server')
        return f'unix:{source}'
    return f'unix:{link}'


def keep_pulse_socket(stop: threading.Event, /) -> None:
    """Keep the audio socket shared: the audio server may restart, the group access may be reset."""
    while not stop.wait(PULSE_CHECK_EVERY):
        if (account := _client_account()) is not None and running():
            share_pulse_socket(account)


def launch() -> str:
    """Start Discord in the background (minimized). Returns '' when started, else the reason.

    The service runs as root, but Electron refuses to, and Discord also needs a D-Bus session: it is
    started as the ``batocera`` user in its own D-Bus session, with the flatpak data of Batocera.
    Its IPC socket appears once it is logged in.
    """
    if running():
        return ''
    command = ['flatpak', 'run', '--system', paths.FLATPAK_APP_ID, '--start-minimized']
    if 'DBUS_SESSION_BUS_ADDRESS' not in os.environ and shutil.which('dbus-run-session'):
        command = ['dbus-run-session', '--', *command]
    env = {**os.environ, 'DISPLAY': os.environ.get('DISPLAY', ':0')}
    uid = gid = groups = None
    if os.geteuid() == 0:
        if (account := _client_account()) is None:
            _logger.error('cannot start Discord: no %s user', paths.DISCORD_USER)
            return f'no {paths.DISCORD_USER} user to run Discord'
        uid, gid = account.pw_uid, account.pw_gid
        groups = os.getgrouplist(account.pw_name, gid)  # audio, video, input...
        runtime_dir = paths.RUN_DIR / 'user' / str(uid)
        xdg = {
            'XDG_DATA_HOME': paths.DISCORD_USER_DIR / '.local' / 'share',
            'XDG_CONFIG_HOME': paths.DISCORD_USER_DIR / '.config',
            'XDG_CACHE_HOME': paths.DISCORD_USER_DIR / '.cache',
        }
        try:
            for directory in (
                runtime_dir,
                paths.FLATPAK_HOME / '.var' / 'app' / paths.FLATPAK_APP_ID,
                paths.DISCORD_USER_DIR,
                paths.DISCORD_USER_DIR / '.local',
                *xdg.values(),
            ):
                _owned_dir(directory, uid, gid)
        except OSError as exc:
            _logger.exception('cannot prepare the directories of Discord')
            return str(exc)
        env = {
            key: value
            for key, value in os.environ.items()
            if key in ('PATH', 'LANG', 'LC_ALL', 'LANGUAGE', 'TZ', 'XAUTHORITY')
        }
        env |= {
            'HOME': str(paths.FLATPAK_HOME),
            'USER': account.pw_name,
            'LOGNAME': account.pw_name,
            'XDG_RUNTIME_DIR': str(runtime_dir),
            **{key: str(value) for key, value in xdg.items()},
            'PULSE_SERVER': share_pulse_socket(account),
            'DISPLAY': os.environ.get('DISPLAY', ':0'),
        }
    _raise_open_files_limit()
    log = client_log()
    log.parent.mkdir(parents=True, exist_ok=True)
    _logger.info('starting Discord as %s', paths.DISCORD_USER if uid is not None else 'the current user')
    try:
        with log.open('ab') as out:
            subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=out,
                stderr=out,
                env=env,
                cwd=env.get('HOME', '/'),
                user=uid,
                group=gid,
                extra_groups=groups,
                start_new_session=True,
            )
    except PROCESS_ERRORS as exc:
        _logger.exception('cannot start Discord')
        return str(exc)
    return ''


def client_log() -> Path:
    return paths.LOG_FILE.with_name('discord-client.log')


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
