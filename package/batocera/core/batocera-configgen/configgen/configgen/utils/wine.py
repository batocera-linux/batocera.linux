from __future__ import annotations

import logging
import os
import re
import shlex
import shutil
import signal
import subprocess
import time
from contextlib import contextmanager
from dataclasses import InitVar, dataclass, field
from datetime import datetime
from pathlib import Path, PureWindowsPath
from typing import TYPE_CHECKING, Final, Self

from ..batoceraPaths import HOME, SAVES, mkdir_if_not_exists
from ..exceptions import BatoceraException

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable, Mapping, Sequence

_logger = logging.getLogger(__name__)

WINE_BASE: Final = Path('/usr/wine')

# where the user drops things of their own: runners, a dxvk build, dlls to import
USER_WINE_DIR: Final = HOME / 'wine'
# a runner unpacked here is picked by name, as it was for batocera-wine
_CUSTOM_RUNNERS: Final = USER_WINE_DIR / 'custom'

WINE_BOTTLES: Final = HOME / 'wine-bottles'

_WINETRICKS: Final = WINE_BASE / 'winetricks'
# where a session leaves its socket, as getLocalXDisplay and getLocalWaylandDisplay
# look for them
_X_SOCKETS: Final = Path('/tmp/.X11-unix')
_WAYLAND_RUNTIME_DIR: Final = Path('/run')
# the display batocera runs on, when no session is to be found at all
_DEFAULT_DISPLAY: Final = ':0.0'
_BSOD: Final = Path('/usr/bin/bsod-wine')
_DXVK: Final = WINE_BASE / 'dxvk'
# a dxvk unpacked here replaces the shipped one, as it did for batocera-wine
_USER_DXVK: Final = USER_WINE_DIR / 'dxvk'

# the windows directory each dxvk build belongs in
_DXVK_ARCHS: Final = (('x64', 'system32'), ('x32', 'syswow64'))
# the same, for the builtin dlls wine ships, used when dxvk is turned off
_BUILTIN_ARCHS: Final = (('x86_64-windows', 'system32'), ('i386-windows', 'syswow64'))
# the direct3d dlls a prefix is given, whether they come from dxvk or from wine
_D3D_DLLS: Final = ('d3d8', 'd3d9', 'd3d10core', 'd3d11', 'd3d12', 'd3d12core', 'dxgi')

# how long to give the wineserver to shut its clients down on its own, before killing it
_WINESERVER_WAIT_TIMEOUT: Final = 10

# how many times, and how far apart, to kill whatever is still holding the prefix
_PREFIX_KILL_ATTEMPTS: Final = 10
_PREFIX_KILL_INTERVAL: Final = 0.2

_PROC: Final = Path('/proc')

# what wine writes at the top of the registry files it creates in a prefix
_ARCH_IN_REGISTRY: Final = re.compile(r'^#arch=(\S+)', re.MULTILINE)

_DEFAULT_WINE_RUNNER: Final = 'wine-tkg'

# what has been installed into a prefix from the import directories of USER_WINE_DIR
_IMPORT_LOG: Final = USER_WINE_DIR / 'imports.log'

# a registry file dropped here is imported into the prefix ahead of the ones of the
# user, as batocera-wine did. It held the raw input setting when batocera-wine wrote it
# itself, and is now whatever put it there wants of the prefix
_RAWINPUT_REG: Final = Path('/var/run/rawinput.reg')


def local_display() -> dict[str, str]:
    """
    The session batocera is running, as the environment to reach it with, for a tool
    called from a shell that has none of its own such as an ssh login.

    X comes first, which is also what a wayland session offers through xwayland, and the
    wayland socket is used when there is no X at all: wine draws through xwayland unless
    it is asked for its own wayland driver, which is what having only WAYLAND_DISPLAY
    tells it to do.
    """
    # the same sockets getLocalXDisplay and getLocalWaylandDisplay pick the first of
    if socket := next(iter(sorted(_X_SOCKETS.glob('X[0-9]*'))), None):
        return {'DISPLAY': f':{socket.name[1:]}'}

    if lock := next(iter(sorted(_WAYLAND_RUNTIME_DIR.glob('wayland-*.lock'))), None):
        # the compositor's socket sits in XDG_RUNTIME_DIR, which an ssh login is without
        return {'WAYLAND_DISPLAY': lock.stem, 'XDG_RUNTIME_DIR': str(_WAYLAND_RUNTIME_DIR)}

    _logger.debug('no X or wayland session found, falling back to %s', _DEFAULT_DISPLAY)

    return {'DISPLAY': _DEFAULT_DISPLAY}


def runner_base(name: str, /) -> tuple[str, Path]:
    """The directory a runner lives in, falling back to the default runner when
    the named one isn't installed. Returns the name actually resolved."""

    if not name:
        return _DEFAULT_WINE_RUNNER, WINE_BASE

    # names batocera-wine accepted for the two shipped runners
    name = {'lutris': 'wine-tkg', 'proton': 'wine-proton'}.get(name, name)

    if (WINE_BASE / name).is_dir():
        return name, WINE_BASE

    if (_CUSTOM_RUNNERS / name).is_dir():
        return name, _CUSTOM_RUNNERS

    _logger.warning("wine runner %s isn't installed, falling back to %s", name, _DEFAULT_WINE_RUNNER)

    return _DEFAULT_WINE_RUNNER, WINE_BASE


def bottle_dir_for(system: str, runner_name: str, rom: Path, /) -> Path:
    """
    Where the prefix of a rom lives. A .wine rom is a prefix already and runs in
    itself, anything else (a .pc directory, a bare .exe, an archive) is given one of
    its own, kept per runner so that changing runner doesn't reuse a prefix built by
    another one.
    """
    # a .wsquashfs reaches us mounted, under a name that no longer says what it is, so
    # a rom that holds a built prefix is taken for one whatever it is called
    if rom.is_dir() and (rom.suffix.lower() == '.wine' or (rom / 'system.reg').is_file()):
        return rom

    return WINE_BOTTLES / system / runner_name / f'{rom.name}.wine'


def prefix_arch(prefix: Path, /) -> str | None:
    """The architecture wine recorded in a prefix, None if it hasn't been built yet."""
    try:
        registry = (prefix / 'userdef.reg').read_text(encoding='utf-8', errors='replace')
    except OSError:
        return None

    if match := _ARCH_IN_REGISTRY.search(registry):
        return match.group(1)

    return None


def wanted_arch(prefix: Path, runner_name: str, /, *, win32: bool = False) -> str | None:
    """
    win32 for a prefix that is to be built as a 32bit one, which only means anything
    while it doesn't exist: a prefix keeps the architecture it was built with.
    """
    if prefix_arch(prefix) is not None:
        return None

    # a runner named win32-something builds 32bit prefixes, as it did for batocera-wine
    if win32 or re.match(r'^win32[-_.]', runner_name, re.IGNORECASE):
        return 'win32'

    return None


def get_autorun_vars(rom: Path, /) -> dict[str, str]:
    # roms built for the batocera-wine era describe themselves in an autorun.cmd,
    # holding the CMD= to run, the DIR= to run it from, and LANG=/ENV= overrides
    autorun = rom / "autorun.cmd"

    if not autorun.is_file():
        return {}

    variables: dict[str, str] = {}

    for line in autorun.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        key, _, value = line.partition('=')
        key = key.strip().upper()
        value = value.strip().strip('"')
        # like batocera-wine did, the first value of a key wins
        if key and value and key not in variables:
            variables[key] = value

    return variables

def resolve_in_rom(rom: Path, name: str, /) -> Path:
    # autorun.cmd holds a windows path, PureWindowsPath takes the separators apart
    return rom.joinpath(*PureWindowsPath(name).parts)

def get_game_dir(rom: Path, /) -> Path:
    # DIR= is the directory the game runs from, and CMD= is relative to it
    if game_dir := get_autorun_vars(rom).get('DIR'):
        if (resolved := resolve_in_rom(rom, game_dir)).is_dir():
            return resolved

        _logger.warning("%s names the directory %s, which doesn't exist", rom / 'autorun.cmd', game_dir)

    return rom

def get_game_command(rom: Path, /) -> tuple[Path, list[str]]:
    """
    What the rom says to run, as the executable and the arguments to pass it. The rom
    names it in its autorun.cmd, we don't guess: a game is free to rename its engine,
    and the other executables next to it are installers and tools.
    """
    autorun = rom / "autorun.cmd"

    if not (cmd := get_autorun_vars(rom).get('CMD')):
        raise BatoceraException(f"{autorun} doesn't exist or doesn't name the CMD to run")

    game_dir = get_game_dir(rom)

    # a CMD is usually just the executable, and may hold spaces without being quoted,
    # so take it whole first and only split it when that names nothing that exists
    if (exe := resolve_in_rom(game_dir, cmd)).is_file():
        return exe, []

    # posix=False keeps the backslashes of a windows path, at the cost of leaving the
    # quotes on the tokens
    tokens = [token.strip('"') for token in shlex.split(cmd, posix=False)]

    if tokens and (exe := resolve_in_rom(game_dir, tokens[0])).is_file():
        return exe, tokens[1:]

    raise BatoceraException(f"The executable {cmd} named by {autorun} doesn't exist in {game_dir}")

def get_game_exe(rom: Path, /) -> Path:
    exe, _ = get_game_command(rom)

    _logger.debug("executable %s from autorun.cmd", exe)

    return exe

def get_autorun_environment(rom: Path, /) -> dict[str, str]:
    """
    The environment a rom asks for in its autorun.cmd: LANG= is the locale to run the
    game in, and ENV= a list of variables, as batocera-wine passed them to the shell.
    """
    variables = get_autorun_vars(rom)
    environment: dict[str, str] = {}

    if lang := variables.get('LANG'):
        environment['LC_ALL'] = lang

    for assignment in shlex.split(variables.get('ENV', '')):
        name, separator, value = assignment.partition('=')
        if separator:
            environment[name] = value

    return environment


def link_saves(rom_dir: Path, prefix: Path, system_saves: Path, /) -> None:
    """
    Keep what the game saves in /userdata/saves rather than inside the prefix, so that
    it survives the prefix being rebuilt and is backed up with the rest of the saves.
    The rom asks for it in its autorun.cmd, with either a SAVEDIR= directory or a
    SAVEFILES= list of files, both relative to the prefix.
    """
    variables = get_autorun_vars(rom_dir)
    save_dir = variables.get('SAVEDIR')
    save_files = variables.get('SAVEFILES')

    if not save_dir and not save_files:
        return

    mkdir_if_not_exists(system_saves)

    if save_dir:
        target = resolve_in_rom(prefix, save_dir)

        if target.is_symlink():
            return

        # the prefix already holds saves, they move to /userdata/saves once
        if target.is_dir():
            shutil.copytree(target, system_saves, dirs_exist_ok=True)
            shutil.rmtree(target)

        mkdir_if_not_exists(target.parent)
        target.symlink_to(system_saves)
        _logger.debug('saves: %s -> %s', target, system_saves)
        return

    for name in save_files.split(';'):
        if not (name := name.strip()):
            continue

        target = resolve_in_rom(prefix, name)
        saved = system_saves / target.name

        if target.is_symlink():
            target.unlink()
        elif target.exists():
            # the prefix already holds the save, it moves to /userdata/saves once
            if saved.exists():
                target.unlink()
            else:
                mkdir_if_not_exists(saved.parent)
                shutil.move(target, saved)

        mkdir_if_not_exists(target.parent)
        target.symlink_to(saved)
        _logger.debug('saves: %s -> %s', target, saved)


# executables that are in a prefix without being the game: the installers that put the
# game there, and what windows itself brings
_NOT_THE_GAME: Final = (
    re.compile(r'/Windows Media Player/'),
    re.compile(r'/Windows NT/'),
    re.compile(r'/Internet Explorer/'),
    re.compile(r'/drive_c/windows/'),
    re.compile(r'/unins[a-z0-9]{0,6}\.exe$', re.IGNORECASE),
    re.compile(r'/install(..)?\.exe$', re.IGNORECASE),
    re.compile(r'/setup\.exe$', re.IGNORECASE),
    re.compile(r'/unwise(..)?\.exe$', re.IGNORECASE),
)

# where the user may add patterns of their own, one regex per line
_AUTORUN_REGEX_FILES: Final = (
    Path('/userdata/roms/windows_installers/autorun-regex.txt'),
    SAVES / 'windows_installers' / 'autorun-regex.txt',
)


def _user_autorun_filters() -> list[re.Pattern[str]]:
    for regex_file in _AUTORUN_REGEX_FILES:
        if not regex_file.is_file():
            continue

        filters: list[re.Pattern[str]] = []

        for line in regex_file.read_text(encoding='utf-8-sig', errors='replace').splitlines():
            # the file documents itself in #-comments, and blank lines separate them
            if not (line := line.strip()) or line.startswith(('#', '*')):
                continue

            try:
                filters.append(re.compile(line))
            except re.error as e:
                _logger.warning('%s: ignoring the pattern %s: %s', regex_file, line, e)

        return filters

    return []


def find_game_executables(directory: Path, file_mask: str = 'drive_c/P*', /) -> list[Path]:
    """
    The executables of a prefix or a game directory that could be the game itself,
    relative to it, in the order they should be offered. file_mask is a glob narrowing
    the search, defaulting to the Program Files directories an installer writes to.
    """
    filters = [*_user_autorun_filters(), *_NOT_THE_GAME]

    executables: list[Path] = []

    for base in sorted(directory.glob(file_mask)) if file_mask not in ('', '.') else [directory]:
        if base.is_file():
            candidates: Iterable[Path] = [base]
        else:
            candidates = base.rglob('*')

        for candidate in candidates:
            if candidate.suffix.lower() != '.exe' or not candidate.is_file():
                continue

            relative = candidate.relative_to(directory)

            if not any(pattern.search(f'/{relative}') for pattern in filters):
                executables.append(relative)

    return sorted(executables)


def write_autorun_cmd(directory: Path, executable: Path | None, /) -> None:
    """
    Describe a game in the autorun.cmd of its directory, so that the wine generator
    knows what to run. Without an executable, write the commented-out template
    batocera-wine wrote, for the user to fill in themselves.
    """
    autorun = directory / 'autorun.cmd'

    if autorun.exists():
        backup = autorun.with_name(f'{autorun.name}.bak')
        _logger.debug('%s exists, keeping it as %s', autorun, backup)
        shutil.move(autorun, backup)

    if executable is None:
        autorun.write_text('#DIR=drive_c/Program Files/myprogram\n#CMD=start.exe\n')
        return

    autorun.write_text(f'DIR={executable.parent}\nCMD="{executable.name}"\n')
    _logger.debug('%s names %s', autorun, executable)


def prefix_holders(prefix: Path, /) -> list[int]:
    """The processes still running in a prefix, our own excepted."""
    # the whole KEY=VALUE record has to match: a substring search would also find
    # the processes of a bottle whose name merely starts with this one's
    wanted = f'WINEPREFIX={prefix}'.encode()
    own_pid = os.getpid()
    holders: list[int] = []

    for entry in _PROC.iterdir():
        if not entry.name.isdigit() or int(entry.name) == own_pid:
            continue

        try:
            environ = (entry / 'environ').read_bytes()
        except OSError:
            # the process is gone, or is one we may not look at
            continue

        if wanted in environ.split(b'\0'):
            holders.append(int(entry.name))

    return holders


def running_prefixes() -> dict[Path, Path | None]:
    """
    The prefixes something is running in, each with the wineserver serving it when one
    of its processes is that wineserver.
    """
    prefixes: dict[Path, Path | None] = {}
    own_pid = os.getpid()

    for entry in _PROC.iterdir():
        if not entry.name.isdigit() or int(entry.name) == own_pid:
            continue

        try:
            environ = (entry / 'environ').read_bytes()
        except OSError:
            continue

        for record in environ.split(b'\0'):
            if not record.startswith(b'WINEPREFIX='):
                continue

            prefix = Path(os.fsdecode(record.removeprefix(b'WINEPREFIX=')))
            prefixes.setdefault(prefix, None)

            try:
                executable = (entry / 'exe').readlink()
            except OSError:
                continue

            if executable.name == 'wineserver':
                prefixes[prefix] = executable

            break

    return prefixes


def stop_all() -> None:
    """
    Ask every running game to close, which is what the exit hotkey does. Each prefix is
    handed to its own wineserver so that a game running under another runner is stopped
    by the wineserver that started it.
    """
    prefixes = running_prefixes()

    if not prefixes:
        _logger.debug('no wine prefix is running')
        return

    for prefix, wineserver in prefixes.items():
        _logger.debug('stopping %s', prefix)

        if wineserver is None:
            # nothing that looks like a wineserver, ask the processes themselves
            for pid in prefix_holders(prefix):
                try:
                    os.kill(pid, signal.SIGTERM)
                except OSError:
                    pass
            continue

        try:
            subprocess.run(
                [wineserver, '-k'],
                env={**os.environ, 'WINEPREFIX': str(prefix)},
                timeout=_WINESERVER_WAIT_TIMEOUT,
                check=False,
            )
        except (subprocess.TimeoutExpired, OSError) as e:
            _logger.warning('%s -k failed for %s: %s', wineserver, prefix, e)


@contextmanager
def mount_iso(image: Path, /) -> Generator[Path]:
    """An installer image, mounted for as long as the installer needs it."""
    mount_point = Path('/var/run/wine') / f'{image.name}.cdrom'
    mount_point.mkdir(parents=True, exist_ok=True)

    for filesystem in ('iso9660', 'udf'):
        if subprocess.call(['mount', '-t', filesystem, image, mount_point]) == 0:
            break
    else:
        mount_point.rmdir()
        raise BatoceraException(f'Unable to mount the image {image}')

    try:
        yield mount_point
    finally:
        subprocess.call(['umount', '-l', mount_point])
        try:
            mount_point.rmdir()
        except OSError:
            _logger.debug('%s is not empty, leaving it', mount_point)


@dataclass
class Runner:
    name: InitVar[str]
    bottle_name: InitVar[str | None] = None
    # a prefix that already exists, for roms that carry their own
    prefix: InitVar[Path | None] = None
    # win32 to build a 32bit prefix, None to let wine decide
    arch: str | None = None

    runner_name: str = field(init=False)
    bottle_dir: Path = field(init=False)
    wine: Path = field(init=False)
    wine64: Path = field(init=False)
    wineserver: Path = field(init=False)
    msiexec: Path = field(init=False)

    __lib32: Path = field(init=False)
    __lib64: Path = field(init=False)
    __env_path: str = field(init=False)
    __ld_library_path: str = field(init=False)

    def __post_init__(self, name: str, bottle_name: str | None, prefix: Path | None) -> None:
        runner_name, base = runner_base(name)
        wine_path = base / runner_name
        wine_lib = wine_path / 'lib' / 'wine'
        wine_server_bin = wine_path / 'bin'

        # split-arch builds keep a loader per architecture under lib/wine, while
        # wow64-only builds (wine-proton, Wine 11.10+) only ship bin/wine
        wine_bin = wine_lib / 'i386-unix'
        wine64_bin = wine_lib / 'x86_64-unix'

        # only a split-arch build has a real WINEARCH=win32 mode: a wow64-only one
        # doesn't have one and doesn't need it, it runs 32bit exes in its own prefix
        supports_win32 = (wine_bin / 'wine').exists()

        if runner_name != 'wine-proton' and supports_win32:
            wine = wine_bin / 'wine'
            wine64 = wine64_bin / 'wine64'

            # Fallback for Wine 11.10+ where wine64 does not exist
            if not wine64.exists():
                wine64 = wine
                env_path = f'{wine_bin}:{wine_server_bin}:/bin:/usr/bin'
            else:
                env_path = f'{wine_bin}:{wine64_bin}:{wine_server_bin}:/bin:/usr/bin'
        else:
            wine = wine_server_bin / 'wine'
            wine64 = wine_server_bin / 'wine64'

            # Fallback for Wine 11.10+ where wine64 does not exist
            if not wine64.exists():
                wine64 = wine

            env_path = f'{wine_server_bin}:/bin:/usr/bin'

        if prefix is not None:
            bottle_dir = prefix
        elif bottle_name is not None:
            bottle_dir = WINE_BOTTLES / bottle_name
        else:
            raise BatoceraException('A wine runner needs either a bottle name or a prefix')

        # a build may split its windows dlls per architecture, or keep both under lib
        lib64 = wine_path / 'lib64' / 'wine'
        lib32 = wine_path / 'lib32' / 'wine'

        self.runner_name = runner_name
        self.wine = wine
        self.wine64 = wine64
        self.wineserver = wine_server_bin / 'wineserver'
        self.msiexec = wine_server_bin / 'msiexec'
        self.bottle_dir = bottle_dir
        self.__lib64 = lib64 = lib64 if lib64.is_dir() else wine_lib
        self.__lib32 = lib32 = lib32 if lib32.is_dir() else wine_lib
        self.__env_path = env_path
        self.__ld_library_path = f'/lib32:{lib32}/i386-unix:/lib:/usr/lib:{lib64}/x86_64-unix'

        # an existing prefix keeps the architecture it was built with, whatever was asked
        if (built_as := prefix_arch(bottle_dir)) is not None:
            if self.arch is not None and self.arch != built_as:
                _logger.info('%s was built as %s, keeping it', bottle_dir, built_as)
            self.arch = built_as

        if self.arch == 'win32' and not supports_win32:
            if built_as == 'win32':
                raise BatoceraException(
                    f'{bottle_dir} is a win32 prefix but {runner_name} has no win32 mode anymore: '
                    'delete and recreate it, or go back to a runner that has one'
                )

            # a 32bit prefix was asked for a runner that has no such thing, ignore it:
            # 32bit games still run, through wow64
            _logger.info('%s has no win32 mode, building a win64 prefix instead', runner_name)
            self.arch = None

    def run_in_prefix(
        self,
        cmd: Sequence[str | Path],
        /, *,
        environment: Mapping[str, str | Path] | None = None,
        wait: bool = True,
        capture_output: bool = True,
    ) -> None:
        """
        Run something in the prefix and, unless told otherwise, wait for the wineserver
        to be done with it before returning.

        What it writes goes to the log, unless capture_output is off: something that
        talks to whoever started it, such as winetricks downloading, keeps the terminal.
        """
        env: dict[str, str | Path] = {**os.environ}

        env.update({
            'LD_LIBRARY_PATH': self.__ld_library_path,
            'WINEPREFIX': self.bottle_dir,
            'PATH': self.__env_path,
        })

        if self.arch:
            env['WINEARCH'] = self.arch

        if environment:
            env.update(environment)

        _logger.debug('command: %s', cmd)

        pipe = subprocess.PIPE if capture_output else None

        proc = subprocess.Popen(cmd, env=env, stdout=pipe, stderr=pipe)
        out, err = proc.communicate()

        if capture_output:
            for stream in (out, err):
                if text := stream.decode(errors='backslashreplace').strip():
                    _logger.debug('%s', text)

        # only what failed is worth an error, wine writes to stderr all the time
        if proc.returncode:
            _logger.error('%s exited with %s', Path(cmd[0]).name, proc.returncode)

        if wait:
            self.wait()

    def wait(self, /) -> None:
        """Wait for the wineserver to be done with whatever was started in the prefix."""
        try:
            subprocess.run(
                [self.wineserver, '-w'],
                env={**os.environ, 'WINEPREFIX': str(self.bottle_dir), 'PATH': self.__env_path},
                timeout=_WINESERVER_WAIT_TIMEOUT,
                check=False,
            )
        except (subprocess.TimeoutExpired, OSError) as e:
            _logger.warning('wineserver -w failed for %s: %s', self.bottle_dir, e)

    def create_bottle(self, /) -> None:
        # nothing to do, the prefix is already bootstrapped
        if (self.bottle_dir / 'system.reg').exists():
            return

        self.bottle_dir.mkdir(parents=True, exist_ok=True)

        # show a please wait screen, bootstrapping a prefix takes a while
        splash = None
        if _BSOD.exists():
            splash = subprocess.Popen([_BSOD])

        try:
            # winegstreamer is disabled, it makes the bootstrap hang when wine debug is on
            self.run_in_prefix([self.wine, 'hostname'], environment={'WINEDLLOVERRIDES': 'winegstreamer='})
        finally:
            if splash is not None:
                splash.terminate()

        if not (self.bottle_dir / 'system.reg').exists():
            shutil.rmtree(self.bottle_dir, ignore_errors=True)
            raise BatoceraException(f'Failed initialising the wine prefix {self.bottle_dir}')

    def game_command(self, game_exe: Path, /) -> list[str | Path]:
        return [self.wine, game_exe]

    @contextmanager
    def running(self, /) -> Generator[None]:
        # a rom on a squashfs is unmounted the moment the game is over, so leaving this
        # block may only return once nothing is left holding it, which is what
        # batocera-wine's stopWineServer did: wine hands the game over to the wineserver
        # and exits long before the game does, and a game that was killed rather than
        # closed leaves wine processes behind that the wineserver won't reap
        try:
            yield
        finally:
            self.__stop_wineserver()
            self.__kill_prefix_holders()

    def __stop_wineserver(self, /) -> None:
        env = {**os.environ, 'WINEPREFIX': str(self.bottle_dir), 'PATH': self.__env_path}

        try:
            # -w waits for the prefix to be done with, and returns once it is
            subprocess.run([self.wineserver, '-w'], env=env, timeout=_WINESERVER_WAIT_TIMEOUT, check=False)
        except subprocess.TimeoutExpired:
            # it isn't going to finish on its own, tell it to kill its clients
            _logger.debug('wineserver -w timed out for %s, killing the prefix', self.bottle_dir)
            try:
                subprocess.run([self.wineserver, '-k'], env=env, timeout=_WINESERVER_WAIT_TIMEOUT, check=False)
            except (subprocess.TimeoutExpired, OSError) as e:
                _logger.warning('wineserver -k failed for %s: %s', self.bottle_dir, e)
        except OSError as e:
            _logger.warning('wineserver -w failed for %s: %s', self.bottle_dir, e)

    def __kill_prefix_holders(self, /) -> None:
        for _ in range(_PREFIX_KILL_ATTEMPTS):
            if not (holders := prefix_holders(self.bottle_dir)):
                return

            _logger.debug('killing %s still holding %s', holders, self.bottle_dir)

            for pid in holders:
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    # already gone, or not ours to kill
                    pass

            time.sleep(_PREFIX_KILL_INTERVAL)

        if holders := prefix_holders(self.bottle_dir):
            _logger.warning('%s is still held by %s', self.bottle_dir, holders)

    def __link_dlls(self, source_dir: Path, windows_dir: str, dlls: Iterable[Path], /) -> set[str]:
        target_dir = self.bottle_dir / 'drive_c' / 'windows' / windows_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        linked: set[str] = set()

        for dll in sorted(dlls):
            link = target_dir / dll.name

            # wine puts its own builtin dll there when it bootstraps the prefix
            if link.is_symlink() or link.exists():
                link.unlink()

            link.symlink_to(dll)
            linked.add(dll.stem)

        if linked:
            _logger.debug('linked %s from %s into %s', ', '.join(sorted(linked)), source_dir, target_dir)

        return linked

    def install_dxvk(self, /) -> set[str]:
        # dxvk isn't built for every architecture, and the dlls it ships change between
        # releases, so link whatever is actually there rather than a hardcoded list:
        # symlinking a missing dll would leave a dangling link that wine cannot load
        overridden: set[str] = set()

        dxvk = _USER_DXVK if _USER_DXVK.is_dir() else _DXVK

        for arch, windows_dir in _DXVK_ARCHS:
            source_dir = dxvk / arch

            if not source_dir.is_dir():
                continue

            overridden |= self.__link_dlls(source_dir, windows_dir, source_dir.glob('*.dll'))

        return overridden

    def install_builtin_d3d(self, /) -> set[str]:
        """
        Point the direct3d dlls of the prefix back at the ones wine ships, for a game
        that is to run on wined3d rather than on dxvk. A prefix that ran with dxvk still
        holds links into the dxvk build, so they have to be replaced, not just left out.
        """
        installed: set[str] = set()

        for arch, windows_dir in _BUILTIN_ARCHS:
            source_dir = (self.__lib64 if windows_dir == 'system32' else self.__lib32) / arch

            if not source_dir.is_dir():
                continue

            dlls = [dll for name in _D3D_DLLS if (dll := source_dir / f'{name}.dll').is_file()]

            installed |= self.__link_dlls(source_dir, windows_dir, dlls)

        return installed

    def install_wine_trick(
        self,
        name: str,
        /, *,
        environment: Mapping[str, str | Path] | None = None
    ) -> None:
        done_file = self.bottle_dir / f'{name}.done'

        if done_file.exists():
            return

        self.run_winetricks(['-q', name], environment=environment)

        done_file.write_text('done')

    def run_winetricks(
        self,
        arguments: Sequence[str],
        /, *,
        environment: Mapping[str, str | Path] | None = None,
        capture_output: bool = True,
    ) -> None:
        if not _WINETRICKS.exists():
            raise BatoceraException(f'{_WINETRICKS} is missing, winetricks is not installed')

        environment = dict(environment or {})

        # a trick installs through the installer of the redist, which wants a display:
        # called over ssh there is none, so it is given the session batocera runs
        if not any(
            environment.get(name) or os.environ.get(name) for name in ('DISPLAY', 'WAYLAND_DISPLAY')
        ):
            display = local_display()
            _logger.debug('no display in the environment, using %s', display)
            environment.update(display)

        self.run_in_prefix(
            [_WINETRICKS, *arguments], environment=environment, capture_output=capture_output
        )

    def regedit(self, file: Path, /) -> None:
        """Import a registry file, into both architectures of the prefix."""
        # //?/unix/... is how wine is given a linux path where it expects a windows one
        for wine in {self.wine, self.wine64}:
            self.run_in_prefix([wine, 'regedit', f'//?/unix{file}'])

    def set_registry_value(self, key: str, name: str, value_type: str, value: str, /) -> None:
        self.run_in_prefix([self.wine, 'reg', 'add', key, '/v', name, '/t', value_type, '/d', value, '/f'])

    def sandbox_prefix(self, /) -> None:
        """
        Replace the links wine puts in the user directories of a prefix by directories
        of their own, so that a game saving to My Documents writes inside the prefix
        rather than all over /userdata/system.
        """
        users = self.bottle_dir / 'drive_c' / 'users'

        if not users.is_dir():
            return

        # don't create every directory: linking Music and My Music both is what wine
        # avoids by shipping the one its version uses
        for user in users.iterdir():
            for name in (
                'Downloads', 'Documents', 'My Documents', 'Music', 'My Music',
                'Pictures', 'My Pictures', 'Videos', 'My Videos', 'Templates',
            ):
                directory = user / name

                if directory.is_symlink():
                    directory.unlink()
                    directory.mkdir(parents=True, exist_ok=True)
                    _logger.debug('sandboxed %s', directory)

    def __import_files(self, name: str, suffixes: Iterable[str], /) -> list[Path]:
        """
        The files the user dropped in /userdata/system/wine/<name> for the prefix to
        take in. They are moved to installed.<name> once they have been, so that they
        are only imported once.
        """
        source_dir = USER_WINE_DIR / name

        if not source_dir.is_dir():
            return []

        wanted = {suffix.lower() for suffix in suffixes}
        files = sorted(
            file for file in source_dir.iterdir()
            if file.is_file() and file.suffix.lower() in wanted
        )

        if not files:
            # nothing of ours in there, and an empty directory is just noise
            try:
                source_dir.rmdir()
            except OSError:
                _logger.warning('%s holds files that are not %s, leaving them', source_dir, ' or '.join(wanted))

        return files

    def __imported(self, file: Path, name: str, /) -> None:
        installed_dir = USER_WINE_DIR / f'installed.{name}'
        installed_dir.mkdir(parents=True, exist_ok=True)

        target = installed_dir / file.name

        # keep whatever is already there, the file may be a newer build of the same thing
        if target.exists():
            target = installed_dir / f'{file.name}.{datetime.now():%y%m%d-%H%M%S}'

        shutil.move(file, target)

        with _IMPORT_LOG.open('a') as log:
            log.write(f'{datetime.now():%D %T} - Installed: {file} --> {self.bottle_dir}\n')

        _logger.debug('imported %s into %s', file, self.bottle_dir)

    def install_redists(self, /) -> None:
        """Run the redistributables the user dropped in /userdata/system/wine/exe."""
        for installer in self.__import_files('exe', ['.exe']):
            match installer.name.lower():
                case 'dxsetup.exe':
                    arguments = ['/silent']
                case name if name.startswith('vcredist_') and ('2005' in name or '2008' in name):
                    arguments = ['/q']
                case name if name.startswith('vcredist_'):
                    arguments = ['/quiet', '/qn', '/norestart']
                case 'oalinst.exe':
                    arguments = ['/s']
                case _:
                    arguments = []

            _logger.info('installing %s', installer)
            self.run_in_prefix([self.wine, installer, *arguments])
            self.__imported(installer, 'exe')

    def install_msis(self, /) -> None:
        """Install the msi packages the user dropped in /userdata/system/wine/msi."""
        for package in self.__import_files('msi', ['.msi']):
            _logger.info('installing %s', package)
            self.run_in_prefix([self.msiexec, '-i', package, '/quiet', '/qn', '/norestart'])
            self.__imported(package, 'msi')

    def install_regs(self, /) -> None:
        """Import the registry files the user dropped in /userdata/system/wine/regs."""
        for registry in self.__import_files('regs', ['.reg']):
            _logger.info('importing %s', registry)
            self.regedit(registry)
            self.__imported(registry, 'regs')

    def install_fonts(self, /) -> None:
        """Add the fonts the user dropped in /userdata/system/wine/fonts to the prefix."""
        fonts_dir = self.bottle_dir / 'drive_c' / 'windows' / 'Fonts'

        for font in self.__import_files('fonts', ['.ttf', '.ttc']):
            fonts_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(font, fonts_dir / font.name)
            self.__imported(font, 'fonts')

    def install_rawinput(self, /) -> None:
        """Import /var/run/rawinput.reg into the prefix, if something left one there."""
        if _RAWINPUT_REG.is_file():
            self.regedit(_RAWINPUT_REG)
            _RAWINPUT_REG.unlink()

    def set_hidraw(self, enabled: bool, /) -> None:
        """
        Let wine read gamepads through hidraw, which modern games need for the extra
        features of a controller, and which breaks older x-input only ones.
        """
        wanted = f'"DisableHidraw"=dword:{0 if enabled else 1:08d}'

        try:
            registry = (self.bottle_dir / 'system.reg').read_text(encoding='utf-8', errors='replace')
        except OSError:
            registry = ''

        # writing it costs a wine start, so only do it when it isn't already set
        if wanted in registry:
            return

        self.set_registry_value(
            r'HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\winebus',
            'DisableHidraw', 'REG_DWORD', '0' if enabled else '1',
        )

    def get_environment(self, /) -> dict[str, str | Path]:
        environment: dict[str, str | Path] = {
            'WINEPREFIX': self.bottle_dir,
            'LD_LIBRARY_PATH': self.__ld_library_path,
            'WINEDLLPATH': f'{self.__lib32}/i386-windows:{self.__lib64}/x86_64-windows',
            'LIBGL_DRIVERS_PATH': '/lib32/dri:/usr/lib/dri',
            'GST_PLUGIN_SYSTEM_PATH_1_0': '/usr/lib/gstreamer-1.0:/lib32/gstreamer-1.0',
            # hum pw 0.2 and 0.3 are hardcoded, not nice
            'SPA_PLUGIN_DIR': '/usr/lib/spa-0.2:/lib32/spa-0.2',
            'PIPEWIRE_MODULE_DIR': '/usr/lib/pipewire-0.3:/lib32/pipewire-0.3',
            # so that the game finds the wineserver and the tools of its own runner
            'PATH': f'{self.wineserver.parent}:{os.environ.get("PATH", "/bin:/usr/bin")}',
        }

        if self.arch:
            environment['WINEARCH'] = self.arch

        return environment

    @classmethod
    def default(cls, bottle_dir: str, /) -> Self:
        return cls(_DEFAULT_WINE_RUNNER, bottle_dir)

    @classmethod
    def for_prefix(cls, name: str | None, prefix: Path, /, *, arch: str | None = None) -> Self:
        """A runner for a prefix that already exists, such as one mounted from a rom."""
        return cls(name or _DEFAULT_WINE_RUNNER, prefix=prefix, arch=arch)
