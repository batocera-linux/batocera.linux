from __future__ import annotations

import functools
import logging
import os
import re
import resource
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

from batocera_common.key_value_config import KeyValueConfig
from batocera_common.paths import BATOCERA_CONF, CACHE, HOME, ROMS, SAVES
from batocera_launch import BatoceraException

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable, Mapping, Sequence

_logger = logging.getLogger(__name__)

WINE_BASE: Final = Path('/usr/wine')

# where the user drops things of their own: runners, a dxvk build, dlls to import
USER_WINE_DIR: Final = HOME / 'wine'
# a runner unpacked here is picked by name, as it was for batocera-wine
_CUSTOM_RUNNERS: Final = USER_WINE_DIR / 'custom'

WINE_BOTTLES_DIR: Final = HOME / 'wine-bottles'

_WINETRICKS_CMD: Final = WINE_BASE / 'winetricks'
_SYSTEM_DXVK_DIR: Final = WINE_BASE / 'dxvk'
# a dxvk unpacked here replaces the shipped one, as it did for batocera-wine
_USER_DXVK_DIR: Final = USER_WINE_DIR / 'dxvk'

# how a runner names its two architectures, and where each belongs in a prefix
_RUNNER_ARCHS_WINDOWS_DIR_MAPPING: Final = (('x86_64-windows', 'system32'), ('i386-windows', 'syswow64'))

# how long to give the wineserver to shut its clients down on its own, before killing it
_WINESERVER_WAIT_TIMEOUT: Final = 10

_PROC: Final = Path('/proc')


_DEFAULT_WINE_RUNNER: Final = 'wine-tkg'

# what has been installed into a prefix from the import directories of USER_WINE_DIR
_IMPORT_LOG: Final = USER_WINE_DIR / 'imports.log'

# a registry file dropped here is imported ahead of the ones of the user
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
    # the sockets getLocalXDisplay and getLocalWaylandDisplay pick the first of
    if socket := next(iter(sorted(Path('/tmp/.X11-unix').glob('X[0-9]*'))), None):
        return {'DISPLAY': f':{socket.name[1:]}'}

    wayland_runtime_dir = Path('/run')

    if lock := next(iter(sorted(wayland_runtime_dir.glob('wayland-*.lock'))), None):
        # the compositor's socket sits in XDG_RUNTIME_DIR, which an ssh login is without
        return {'WAYLAND_DISPLAY': lock.stem, 'XDG_RUNTIME_DIR': str(wayland_runtime_dir)}

    # the display batocera runs on, when no session is to be found at all
    _logger.debug('no X or wayland session found, falling back to :0.0')

    return {'DISPLAY': ':0.0'}


def _mount_table() -> list[tuple[Path, str, str]]:
    """Where the system has something mounted, deepest mount first, each with the
    filesystem it holds and what it was mounted from."""
    mounts: list[tuple[Path, str, str]] = []

    mountinfo = _PROC / 'self' / 'mountinfo'

    try:
        table = mountinfo.read_text(encoding='utf-8', errors='replace')
    except OSError as e:
        _logger.debug('unable to read %s: %s', mountinfo, e)
        return mounts

    for line in table.splitlines():
        mount, separator, filesystem = line.partition(' - ')

        if not separator:
            continue

        mount_fields = mount.split(' ')
        filesystem_fields = filesystem.split(' ')

        if len(mount_fields) < 5 or len(filesystem_fields) < 2:
            continue

        mounts.append(
            (
                Path(_unescape_mount(mount_fields[4])),
                filesystem_fields[0],
                _unescape_mount(filesystem_fields[1]),
            )
        )

    return sorted(mounts, key=lambda mount: len(mount[0].parts), reverse=True)


def _unescape_mount(field: str, /) -> str:
    # mountinfo writes what would break its fields as a \ooo octal escape
    return re.sub(r'\\(\d{3})', lambda escape: chr(int(escape.group(1), 8)), field)


def find_path_mount(path: Path, /) -> tuple[str, Path, str] | None:

    existing = path

    while not existing.exists() and existing != existing.parent:
        existing = existing.parent

    try:
        resolved = existing.resolve()
    except OSError:
        resolved = existing

    for mount_point, filesystem, source in _mount_table():
        if resolved == mount_point or mount_point in resolved.parents:
            return filesystem, mount_point, source

    return None


def log_filesystems(*paths: Path) -> None:
    """
    Report what each of these is and what filesystem it lives on.
    """
    for path in dict.fromkeys(paths):
        if path.is_symlink() and not path.exists():
            _logger.info('%s is a link to %s, which is not there', path, path.readlink())
            continue

        if (mount := find_path_mount(path)) is None:
            where = 'an unknown filesystem'
        else:
            filesystem, mount_point, source = mount
            where = f'{filesystem}, {source} mounted on {mount_point}'

        if not path.exists():
            _logger.info('%s is not there yet, and belongs on %s', path, where)
            continue

        link = f', linked to {path.readlink()}' if path.is_symlink() else ''
        kind = 'directory' if path.is_dir() else 'file'

        _logger.info('%s %s is on %s%s', kind, path, where, link)


def get_runner_name(name: str, /) -> str:
    if not name:
        return _DEFAULT_WINE_RUNNER

    # names batocera-wine accepted for the two shipped runners
    name = {'lutris': 'wine-tkg', 'proton': 'wine-proton'}.get(name, name)

    if any((base / name).is_dir() for base in (WINE_BASE, _CUSTOM_RUNNERS)):
        return name

    _logger.warning("wine runner %s isn't installed, falling back to %s", name, _DEFAULT_WINE_RUNNER)

    return _DEFAULT_WINE_RUNNER


def get_runner_path(name: str, /) -> Path:
    runner_name = get_runner_name(name)

    for base in (WINE_BASE, _CUSTOM_RUNNERS):
        if (path := base / runner_name).is_dir():
            return path

    return WINE_BASE / runner_name


def get_prefix_path(system: str, runner_name: str, rom: Path, /) -> Path:
    """
    Where the prefix of a rom lives. A .wine rom is a prefix already and runs in
    itself, anything else (a .pc directory, a bare .exe, an archive) is given one of
    its own, kept per runner so that changing runner doesn't reuse a prefix built by
    another one.
    """
    # a .wsquashfs reaches us mounted, so a rom holding a prefix is one whatever its name
    if rom.is_dir() and (rom.suffix.lower() == '.wine' or (rom / 'system.reg').is_file()):
        return rom

    return WINE_BOTTLES_DIR / system / runner_name / f'{rom.name}.wine'


def current_prefix_arch(prefix: Path, /) -> str | None:
    """The architecture wine recorded in a prefix, None if it hasn't been built yet."""
    try:
        registry = (prefix / 'userdef.reg').read_text(encoding='utf-8', errors='replace')
    except OSError:
        return None

    # what wine writes at the top of the registry files it creates in a prefix
    if match := re.search(r'^#arch=(\S+)', registry, re.MULTILINE):
        return match.group(1)

    return None


def wanted_prefix_arch(runner_name: str, /, *, enable_win32: bool = False) -> str | None:
    """
    win32 when anything asks for a 32bit prefix, which only means something while the
    prefix doesn't exist: a prefix keeps the architecture it was built with, and Runner
    is what reconciles this with one that is already there.
    """
    if enable_win32:
        _logger.info('a 32bit prefix is asked for, enable_win32 is on')
        return 'win32'

    # a runner named win32-something builds 32bit prefixes, as it did for batocera-wine
    if re.match(r'^win32[-_.]', runner_name, re.IGNORECASE):
        _logger.info('a 32bit prefix is asked for, the runner %s carries win32 in its name', runner_name)
        return 'win32'

    return None


def get_autorun_vars(rom: Path, /) -> dict[str, str]:
    # a rom describes itself in an autorun.cmd: CMD=, DIR=, and LANG=/ENV= overrides
    autorun = rom / 'autorun.cmd'

    if not autorun.is_file():
        return {}

    variables: dict[str, str] = {}

    for line in autorun.read_text(encoding='utf-8-sig', errors='replace').splitlines():
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
    autorun = rom / 'autorun.cmd'

    if not (cmd := get_autorun_vars(rom).get('CMD')):
        raise BatoceraException(f"{autorun} doesn't exist or doesn't name the CMD to run")

    game_dir = get_game_dir(rom)

    # a CMD may hold unquoted spaces, so take it whole before splitting it
    if (exe := resolve_in_rom(game_dir, cmd)).is_file():
        return exe, []

    # posix=False keeps the backslashes of a windows path, at the cost of the quotes
    tokens = [token.strip('"') for token in shlex.split(cmd, posix=False)]

    if tokens and (exe := resolve_in_rom(game_dir, tokens[0])).is_file():
        return exe, tokens[1:]

    raise BatoceraException(f"The executable {cmd} named by {autorun} doesn't exist in {game_dir}")


def get_game_exe(rom: Path, /) -> Path:
    exe, _ = get_game_command(rom)

    _logger.debug('executable %s from autorun.cmd', exe)

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

    if save_dir:
        system_saves.mkdir(parents=True, exist_ok=True)

        target = resolve_in_rom(prefix, save_dir)
        log_filesystems(system_saves, target)

        if target.is_symlink():
            return

        # the prefix already holds saves, they move to /userdata/saves once
        if target.is_dir():
            shutil.copytree(target, system_saves, dirs_exist_ok=True)
            shutil.rmtree(target)

        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(system_saves)
        _logger.debug('saves: %s -> %s', target, system_saves)
        return

    if not save_files:
        return

    system_saves.mkdir(parents=True, exist_ok=True)
    log_filesystems(system_saves, resolve_in_rom(prefix, save_files.partition(';')[0].strip()))

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
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(target, saved)

        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(saved)
        _logger.debug('saves: %s -> %s', target, saved)


# what is in a prefix without being the game: its installers, and windows itself
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
    ROMS / 'windows_installers' / 'autorun-regex.txt',
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
    # the whole record has to match, a bottle whose name starts with this one's is not it
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


def _get_file_path_from_iso(media: Path, name: str, /) -> Path | None:
    """
    The file an autorun.inf names, on the mounted image. iso9660 without rock ridge
    gives its names in upper case and with a version suffix, so nothing can be assumed
    of how the name was written. None when the image holds no such file.
    """
    current = media

    for part in PureWindowsPath(name).parts:
        if part in ('\\', '/'):
            continue

        if (candidate := current / part).exists():
            current = candidate
            continue

        wanted = part.lower()

        try:
            entries = sorted(current.iterdir())
        except OSError:
            return None

        for entry in entries:
            if entry.name.lower().partition(';')[0] == wanted:
                current = entry
                break
        else:
            return None

    return current


def _read_autorun_inf(inf: Path, /) -> dict[str, str]:
    data = inf.read_bytes()

    # a utf-16 one carries a byte order mark, either way round
    if data[:2] in (b'\xff\xfe', b'\xfe\xff'):
        text = data.decode('utf-16', errors='replace')
    else:
        text = data.decode('utf-8-sig', errors='replace')

    section = re.compile(r'\[\s*autorun(?:\.(?P<arch>[^\]\s]+))?\s*\]', re.IGNORECASE)
    sections: dict[str, dict[str, str]] = {}
    entries: dict[str, str] | None = None

    for line in text.splitlines():
        line = line.strip()

        if not line or line.startswith(';'):
            continue

        if line.startswith('['):
            match = section.fullmatch(line)
            entries = sections.setdefault((match.group('arch') or '').lower(), {}) if match else None
            continue

        key, separator, value = line.partition('=')

        if entries is not None and separator and (key := key.strip().lower()) not in entries:
            entries[key] = value.strip()

    # an [autorun.amd64] section is what overrides the plain [autorun] one
    return {**sections.get('', {}), **sections.get('amd64', {})}


def autorun_inf_command(media: Path, drive: str = 'd:', /) -> list[str] | None:
    """
    What the autorun.inf of an installation medium says to run, as a command on the drive
    the medium is mounted as, or None when it names nothing that is there.
    """
    inf = _get_file_path_from_iso(media, 'autorun.inf')

    if inf is None or not inf.is_file():
        return None

    try:
        entries = _read_autorun_inf(inf)
    except OSError as e:
        _logger.warning('unable to read %s: %s', inf, e)
        return None

    # the keys an autorun.inf names what to run with
    for key in ('open', 'shellexecute'):
        if not (value := entries.get(key)):
            continue

        tokens = [token.strip('"') for token in shlex.split(value, posix=False)]

        if not tokens:
            continue

        if (target := _get_file_path_from_iso(media, tokens[0])) is None or not target.is_file():
            _logger.warning('%s names %s, which is not on the medium', inf, tokens[0])
            continue

        return [str(PureWindowsPath(f'{drive}\\', *target.relative_to(media).parts)), *tokens[1:]]

    return None


def display_environment(*, wayland_driver: str = 'xwayland') -> dict[str, str | Path]:
    """
    Wine draws through XWayland unless the game asks for the native wayland driver, in
    which case it is given no DISPLAY at all and picks the wayland driver itself.
    """
    try:
        display_mode = subprocess.run(
            ['batocera-resolution', 'getDisplayMode'],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        ).stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        _logger.warning('unable to tell what the display is running: %s', e)
        display_mode = ''

    if display_mode == 'wayland' and wayland_driver == 'native':
        _logger.debug('wayland with the native driver requested, running without a DISPLAY')
        return {'DISPLAY': ''}

    # x11, or xwayland: give the game the keyboard layout of the system
    if keyboard := KeyValueConfig(BATOCERA_CONF).get('system.kblayout'):
        try:
            subprocess.run(['setxkbmap', keyboard], capture_output=True, check=False)
        except OSError as e:
            _logger.warning('setxkbmap failed: %s', e)

    return {}


def nvidia_prime_environment() -> dict[str, str | Path]:
    """
    What a game needs to draw on the nvidia card of a prime laptop. The session exports
    the GLX offload variables for everything it starts, which is not how a game finds
    its vulkan driver: they go, and the driver is named instead.
    """
    if not Path('/var/tmp/nvidia.prime').exists():
        return {}

    for variable in ('__NV_PRIME_RENDER_OFFLOAD', '__VK_LAYER_NV_optimus', '__GLX_VENDOR_LIBRARY_NAME'):
        os.environ.pop(variable, None)

    # a game running in a prefix may be 32bit, so it is given both drivers
    drivers = '/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json:/usr/share/vulkan/icd.d/nvidia_icd.i686.json'

    return {
        # VK_DRIVER_FILES is what named it before the loader renamed it
        'VK_ICD_FILENAMES': drivers,
        'VK_DRIVER_FILES': drivers,
        'VK_LAYER_PATH': '/usr/share/vulkan/explicit_layer.d',
    }


def dxvk_environment(
    runner: Runner,
    /,
    *,
    enabled: bool = True,
    nvapi: bool = False,
    vkreflex: bool = False,
    hud: bool = False,
    reset_cache: bool = False,
) -> dict[str, str | Path]:
    # Reflex requires NVAPI to function; force it on if Reflex is enabled
    nvapi = nvapi or vkreflex

    environment: dict[str, str | Path] = {
        'DXVK_STATE_CACHE': 'reset' if reset_cache else '1',
        'DXVK_ENABLE_NVAPI': '1' if nvapi else '0',
        'NVAPI': '1' if nvapi else '0',
    }

    if vkreflex:
        environment['DXVK_NVAPI_VKREFLEX'] = '1'
    else:
        environment['DISABLE_DXVK_NVAPI_VKREFLEX'] = '1'

    if hud:
        environment['DXVK_HUD'] = '1'

    if overrides := (runner.install_dxvk(nvapi=nvapi) if enabled else []):
        environment.update(
            {
                'DXVK_ASYNC': '1',
                'DXVK_CONFIG_FILE': USER_WINE_DIR / 'dxvk.conf',
                # the shader cache belongs with the other ones, not beside the game
                'DXVK_STATE_CACHE_PATH': CACHE,
            }
        )
    else:
        environment['DXVK_ASYNC'] = '0'

        # a prefix that ran with dxvk still links into it, put wine's own dlls back
        if builtin := sorted(runner.install_builtin_d3d()):
            overrides.append(f'{",".join(builtin)}=b')

        overrides.append('nvapi64,nvapi=')

    environment['WINEDLLOVERRIDES'] = ';'.join(overrides)

    return environment


def _raise_file_limit() -> None:
    wanted = 1048576

    try:
        _, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        resource.setrlimit(resource.RLIMIT_NOFILE, (min(wanted, hard), hard))
    except (OSError, ValueError) as e:
        _logger.warning('could not raise the file limit, which may impact performance: %s', e)


def _relink(link: Path, target: Path, /) -> None:
    """Point a link at a file, replacing whatever is already there: wine puts its own
    builtin dll where ours goes when it bootstraps the prefix."""
    if link.is_symlink() or link.exists():
        link.unlink()

    link.symlink_to(target)


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
    prefix_dir: Path = field(init=False)
    wine: Path = field(init=False)
    wine64: Path = field(init=False)
    wineserver: Path = field(init=False)
    msiexec: Path = field(init=False)

    __wine_path: Path = field(init=False)
    __lib32: Path = field(init=False)
    __lib64: Path = field(init=False)
    __env_path: str = field(init=False)
    __ld_library_path: str = field(init=False)

    def __post_init__(self, name: str, bottle_name: str | None, prefix: Path | None) -> None:
        runner_name = get_runner_name(name)
        wine_path = get_runner_path(runner_name)
        wine_lib = wine_path / 'lib' / 'wine'
        wine_server_bin = wine_path / 'bin'

        # a split-arch build has a loader per architecture, a wow64-only one only bin/wine
        wine_bin = wine_lib / 'i386-unix'
        wine64_bin = wine_lib / 'x86_64-unix'

        # only a split-arch build has a real WINEARCH=win32 mode, wow64 needs none
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
            prefix_dir = prefix
        elif bottle_name is not None:
            prefix_dir = WINE_BOTTLES_DIR / bottle_name
        else:
            raise BatoceraException('A wine runner needs either a bottle name or a prefix')

        # a build may split its windows dlls per architecture, or keep both under lib
        lib64 = wine_path / 'lib64' / 'wine'
        lib32 = wine_path / 'lib32' / 'wine'

        self.runner_name = runner_name
        self.__wine_path = wine_path
        self.wine = wine
        self.wine64 = wine64
        self.wineserver = wine_server_bin / 'wineserver'
        self.msiexec = wine_server_bin / 'msiexec'
        self.prefix_dir = prefix_dir
        self.__lib64 = lib64 = lib64 if lib64.is_dir() else wine_lib
        self.__lib32 = lib32 = lib32 if lib32.is_dir() else wine_lib
        self.__env_path = env_path
        self.__ld_library_path = f'/lib32:{lib32}/i386-unix:/lib:/usr/lib:{lib64}/x86_64-unix'

        # Append custom runner libs when present (Ge-Proton 11 needs its own ffmpeg)
        if (runner_libs := wine_path / 'lib' / 'x86_64-linux-gnu').is_dir():
            self.__ld_library_path += f'{os.pathsep}{runner_libs}{os.pathsep}{wine_path / "lib" / "i386-linux-gnu"}'

        # a prefix keeps the arch it was built with, and only a 32bit one has to be named
        if (existing_prefix_arch := current_prefix_arch(prefix_dir)) is not None:
            _logger.info('found arch %s recorded in the prefix %s', existing_prefix_arch, prefix_dir)

            if self.arch == 'win32' and existing_prefix_arch != 'win32':
                _logger.warning(
                    'the prefix is %s in the registry, it cannot be turned into a 32bit one: '
                    'delete it to have it rebuilt, or turn enable_win32 off',
                    existing_prefix_arch,
                )

            self.arch = existing_prefix_arch if existing_prefix_arch == 'win32' else None
        elif self.arch is None:
            _logger.info('building the prefix as win64')

        if self.arch == 'win32' and not supports_win32:
            if existing_prefix_arch == 'win32':
                raise BatoceraException(
                    f'{prefix_dir} is a win32 prefix but {runner_name} has no win32 mode anymore: '
                    'delete and recreate it, or go back to a runner that has one'
                )

            # the runner has no win32 mode, ignore it: 32bit games still run through wow64
            _logger.info('%s has no win32 mode, building a win64 prefix instead', runner_name)
            self.arch = None

        # while esync is deprecated, the ulimit is still important for wine performance
        _raise_file_limit()

    def __wine_environment(self, /) -> dict[str, str | Path]:
        """
        What wine needs of its runner, whoever starts it: the game, the installer of a
        redist, winetricks, the bootstrap of a prefix. batocera-wine exported these once
        in init_wine, and so had them in everything it went on to run.
        """
        environment: dict[str, str | Path] = {
            'WINEPREFIX': self.prefix_dir,
            'LD_LIBRARY_PATH': self.__ld_library_path,
            'WINEDLLPATH': f'{self.__lib32}/i386-windows:{self.__lib64}/x86_64-windows',
            'LIBGL_DRIVERS_PATH': '/lib32/dri:/usr/lib/dri',
            'GST_PLUGIN_SYSTEM_PATH_1_0': '/usr/lib/gstreamer-1.0:/lib32/gstreamer-1.0',
            # hum pw 0.2 and 0.3 are hardcoded, not nice
            'SPA_PLUGIN_DIR': '/usr/lib/spa-0.2:/lib32/spa-0.2',
            'PIPEWIRE_MODULE_DIR': '/usr/lib/pipewire-0.3:/lib32/pipewire-0.3',
        }

        if self.arch:
            environment['WINEARCH'] = self.arch

        return environment

    def run_in_prefix(
        self,
        cmd: Sequence[str | Path],
        /,
        *,
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
        env: dict[str, str | Path] = {**os.environ, **self.__wine_environment()}

        env['PATH'] = self.__env_path

        if environment:
            env.update(environment)

        # no start menu entries wanted, and merged so the caller keeps its own overrides
        env['WINEDLLOVERRIDES'] = ';'.join(
            str(override) for override in ('winemenubuilder.exe=', env.get('WINEDLLOVERRIDES')) if override
        )

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
                env={**os.environ, 'WINEPREFIX': str(self.prefix_dir), 'PATH': self.__env_path},
                timeout=_WINESERVER_WAIT_TIMEOUT,
                check=False,
            )
        except (subprocess.TimeoutExpired, OSError) as e:
            _logger.warning('wineserver -w failed for %s: %s', self.prefix_dir, e)

    def create_or_update_prefix(self, /) -> None:
        """
        Build the prefix if it isn't there, and bring an existing one up to the runner
        it is about to run with: a prefix carries the dlls of whichever runner built it,
        and those of a runner that has gone are what keeps it from starting.
        """
        if (self.prefix_dir / 'system.reg').exists():
            self.__update_bottle()
            return

        self.prefix_dir.mkdir(parents=True, exist_ok=True)

        # show a please wait screen, bootstrapping a prefix takes a while
        splash = None
        if (bsod := Path('/usr/bin/bsod-wine')).exists():
            splash = subprocess.Popen([bsod])

        try:
            # winegstreamer is disabled, it makes the bootstrap hang when wine debug is on
            self.run_in_prefix([self.wine, 'wineboot', '-u'], environment={'WINEDLLOVERRIDES': 'winegstreamer='})
        finally:
            if splash is not None:
                splash.terminate()

        if not (self.prefix_dir / 'system.reg').exists():
            shutil.rmtree(self.prefix_dir, ignore_errors=True)
            raise BatoceraException(f'Failed initialising the wine prefix {self.prefix_dir}')

        self.install_runner_libs()
        self.__update_prefix_timestamp()

    def __update_bottle(self, /) -> None:
        """
        Run wineboot over a prefix that was built by another runner, or by an older
        build of this one, which is what the proton scripts do: the dlls a prefix holds
        belong to the runner that put them there.
        """
        if (stamp := self.__get_runner_timestamp()) is None or self.__get_prefix_timestamp() == stamp:
            return

        _logger.info('%s was built with another runner, bringing it up to date', self.prefix_dir)

        # our links are all recreated below
        for _, windows_dir in _RUNNER_ARCHS_WINDOWS_DIR_MAPPING:
            directory = self.prefix_dir / 'drive_c' / 'windows' / windows_dir

            if directory.is_dir():
                for entry in directory.iterdir():
                    if entry.is_symlink():
                        entry.unlink()

        self.install_runner_libs()

        # avoid error if dotnet tricks is installed keeping wine-mono out
        overrides = 'mscoree,mshtml=' if self.__is_dotnet_tricks_installed() else ''

        self.run_in_prefix([self.wine, 'wineboot', '-u'], environment={'WINEDLLOVERRIDES': overrides})

        self.__update_prefix_timestamp()

    def __get_runner_timestamp(self, /) -> str | None:
        """When the wine.inf of the runner was built, which is what wine tells prefixes
        apart by. None for a runner that ships none, which says nothing to compare."""
        try:
            return str(int((self.__wine_path / 'share' / 'wine' / 'wine.inf').stat().st_mtime))
        except OSError:
            return None

    def __get_prefix_timestamp(self, /) -> str | None:
        # what wine writes when it updates a prefix: the mtime of the wine.inf it used
        try:
            return (self.prefix_dir / '.update-timestamp').read_text().strip()
        except OSError:
            return None

    def __update_prefix_timestamp(self, /) -> None:
        # wine writes it only when it updates by itself, else we update every launch
        if (stamp := self.__get_runner_timestamp()) is not None:
            (self.prefix_dir / '.update-timestamp').write_text(f'{stamp}\n')

    def __is_dotnet_tricks_installed(self, /) -> bool:
        try:
            registry = (self.prefix_dir / 'user.reg').read_text(encoding='utf-8', errors='replace')
        except OSError:
            return False

        # how a prefix that had the dotnet tricks installed says it keeps wine-mono out
        return '"*mscoree"="native"' in registry

    # different runners version have different directory layout
    def __dll_dir(self, component: str, arch: str, /) -> Path | None:
        if arch == 'i386-windows':
            lib_dir, alt_dir = self.__lib32, self.__wine_path / 'lib'
        else:
            lib_dir, alt_dir = self.__lib64, self.__wine_path / 'lib64'

        for candidate in (
            self.__lib64 / component / arch,
            self.__wine_path / 'lib' / component / arch,
            lib_dir / component,
            alt_dir / component,
        ):
            if candidate.is_dir():
                return candidate

        return None

    # ge-proton11 force hidraw by default and don't report any gamepad through sdl
    @functools.cached_property
    def forces_hidraw(self) -> bool:
        try:
            winebus = (self.__lib64 / 'x86_64-unix' / 'winebus.so').read_bytes()
        except OSError:
            return False

        # what such a winebus carries, there is nothing else to tell one apart by
        return b'hidraw handles native reports' in winebus

    # wine-tkg && wine-proton link wined3d statically, ge-proton needs libvkd3d && icu
    def install_runner_libs(self, /) -> None:
        # a 32bit prefix has no syswow64 and no 64bit dll, system32 is where its dlls go
        targets = (('i386-windows', 'system32'),) if self.arch == 'win32' else _RUNNER_ARCHS_WINDOWS_DIR_MAPPING

        for arch, windows_dir in targets:
            for component in ('vkd3d', 'icu'):
                if (source_dir := self.__dll_dir(component, arch)) is not None:
                    self.__link_dlls(source_dir, windows_dir, source_dir.glob('*.dll'))

    def game_command(self, game_exe: Path, /) -> list[str | Path]:
        return [self.wine, game_exe]

    def stop(self, /) -> None:
        """
        Close whatever is left running in the prefix, and wait for it to be gone. A rom
        on a squashfs is unmounted the moment the game is over, so this may only return
        once nothing is left holding it, which is what batocera-wine's stopWineServer
        did: wine hands the game over to the wineserver and exits long before the game
        does, and a game that was killed rather than closed leaves wine processes behind
        that the wineserver won't reap.
        """
        self.__stop_wineserver()
        self.__kill_prefix_holders()

    def __stop_wineserver(self, /) -> None:
        env = {**os.environ, 'WINEPREFIX': str(self.prefix_dir), 'PATH': self.__env_path}

        try:
            # -w waits for the prefix to be done with, and returns once it is
            subprocess.run([self.wineserver, '-w'], env=env, timeout=_WINESERVER_WAIT_TIMEOUT, check=False)
        except subprocess.TimeoutExpired:
            # it isn't going to finish on its own, tell it to kill its clients
            _logger.debug('wineserver -w timed out for %s, killing the prefix', self.prefix_dir)
            try:
                subprocess.run([self.wineserver, '-k'], env=env, timeout=_WINESERVER_WAIT_TIMEOUT, check=False)
            except (subprocess.TimeoutExpired, OSError) as e:
                _logger.warning('wineserver -k failed for %s: %s', self.prefix_dir, e)
        except OSError as e:
            _logger.warning('wineserver -w failed for %s: %s', self.prefix_dir, e)

    def __kill_prefix_holders(self, /) -> None:
        # how many times, and how far apart, to kill whatever is still holding the prefix
        for _ in range(10):
            if not (holders := prefix_holders(self.prefix_dir)):
                return

            _logger.debug('killing %s still holding %s', holders, self.prefix_dir)

            for pid in holders:
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    # already gone, or not ours to kill
                    pass

            time.sleep(0.2)

        if holders := prefix_holders(self.prefix_dir):
            _logger.warning('%s is still held by %s', self.prefix_dir, holders)

    def __link_dlls(self, source_dir: Path, windows_dir: str, dlls: Iterable[Path], /) -> set[str]:
        target_dir = self.prefix_dir / 'drive_c' / 'windows' / windows_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        linked: set[str] = set()

        for dll in sorted(dlls):
            _relink(target_dir / dll.name, dll)
            linked.add(dll.stem)

        if linked:
            _logger.debug('linked %s from %s into %s', ', '.join(sorted(linked)), source_dir, target_dir)

        return linked

    def install_dxvk(self, /, *, nvapi: bool = False) -> list[str]:
        """
        Install the direct3d dlls the prefix is to draw through, and say what it is to
        load them as, as the WINEDLLOVERRIDES entries of what went in. Empty when there
        is no dxvk to install at all, which is what says the game is to run on the
        wined3d of wine instead.

        nvapi says whether the game may reach the nvidia driver through them: the dlls
        go in either way, so that a prefix isn't left on the ones of a previous start.
        """
        # a custom runner's own dxvk is what it supports, and is stable across versions
        if self.__dll_dir('dxvk', 'x86_64-windows') is not None:
            installed = self.__install_runner_d3d()
        else:
            # link whatever is there, a hardcoded list would dangle on a missing dll
            installed: set[str] = set()

            dxvk = _USER_DXVK_DIR if _USER_DXVK_DIR.is_dir() else _SYSTEM_DXVK_DIR

            # the windows directory each dxvk build belongs in
            for arch, windows_dir in (('x64', 'system32'), ('x32', 'syswow64')):
                source_dir = dxvk / arch

                if not source_dir.is_dir():
                    continue

                installed |= self.__link_dlls(source_dir, windows_dir, source_dir.glob('*.dll'))

        overrides: list[str] = []

        if graphics := sorted(dll for dll in installed if not dll.startswith(('nvapi', 'nvofapi'))):
            overrides.append(f'{",".join(graphics)}=n')

        # nvapi is named apart, it only means anything on nvidia and is left off elsewhere
        if nvapi_dlls := sorted(dll for dll in installed if dll.startswith(('nvapi', 'nvofapi'))):
            overrides.append(f'{",".join(nvapi_dlls)}={"n" if nvapi else ""}')

        return overrides

    def __install_runner_d3d(self, /) -> set[str]:
        # d3d12 comes from vkd3d-proton, nvapi from dxvk-nvapi, both optional
        overridden: set[str] = set()

        for arch, windows_dir in _RUNNER_ARCHS_WINDOWS_DIR_MAPPING:
            # the direct3d a runner may build itself, each in a directory named after it
            for component in ('dxvk', 'vkd3d-proton', 'nvapi'):
                if (source_dir := self.__dll_dir(component, arch)) is not None:
                    overridden |= self.__link_dlls(source_dir, windows_dir, source_dir.glob('*.dll'))

        return overridden

    def install_d7vk(self, enabled: bool, /) -> bool:
        """Says whether the prefix is to load d7vk, which the dll overrides have to carry."""
        # d7vk translates ddraw to vulkan, 32bit only: syswow64 in win64, system32 in win32
        ddraw_dir = self.prefix_dir / 'drive_c' / 'windows' / ('system32' if self.arch == 'win32' else 'syswow64')
        builtin = self.__lib32 / 'i386-windows' / 'ddraw.dll'

        if enabled and (d7vk := self.__d7vk_dll()) is not None:
            self.__link_dlls(d7vk.parent, ddraw_dir.name, [d7vk])
            # d7vk hands what it doesn't draw to wine's ddraw, under the name it looks for
            if builtin.is_file():
                _relink(ddraw_dir / 'ddraw_.dll', builtin)

            return True

        if enabled:
            _logger.warning('d7vk is not installed, %s is left on the ddraw of wine', self.prefix_dir)

        # a prefix that ran with d7vk still links into it, put wine's own ddraw back
        if builtin.is_file():
            self.__link_dlls(builtin.parent, ddraw_dir.name, [builtin])

        (ddraw_dir / 'ddraw_.dll').unlink(missing_ok=True)

        return False

    def __d7vk_dll(self, /) -> Path | None:
        if (runner_dir := self.__dll_dir('d7vk', 'i386-windows')) is not None:
            candidates = [runner_dir / 'ddraw.dll']
        else:
            # d7vk is 32bit only, and is installed beside the 32bit dlls of dxvk
            candidates = [_USER_DXVK_DIR / 'x32' / 'ddraw.dll', _SYSTEM_DXVK_DIR / 'x32' / 'ddraw.dll']

        return next((candidate for candidate in candidates if candidate.is_file()), None)

    def install_builtin_d3d(self, /) -> set[str]:
        """
        Point the direct3d dlls of the prefix back at the ones wine ships, for a game
        that is to run on wined3d rather than on dxvk. A prefix that ran with dxvk still
        holds links into the dxvk build, so they have to be replaced, not just left out.
        """
        installed: set[str] = set()

        # the builtin dlls wine ships are named and placed as any other of the runner
        for arch, windows_dir in _RUNNER_ARCHS_WINDOWS_DIR_MAPPING:
            source_dir = (self.__lib64 if windows_dir == 'system32' else self.__lib32) / arch

            if not source_dir.is_dir():
                continue

            # the direct3d dlls a prefix is given, whether from dxvk or from wine
            names = ('d3d8', 'd3d9', 'd3d10core', 'd3d11', 'd3d12', 'd3d12core', 'dxgi')
            dlls = [dll for name in names if (dll := source_dir / f'{name}.dll').is_file()]

            installed |= self.__link_dlls(source_dir, windows_dir, dlls)

        return installed

    def install_wine_trick(self, name: str, /, *, environment: Mapping[str, str | Path] | None = None) -> None:
        done_file = self.prefix_dir / f'{name}.done'

        if done_file.exists():
            return

        self.run_winetricks(['-q', name], environment=environment)

        done_file.write_text('done')

    def run_winetricks(
        self,
        arguments: Sequence[str],
        /,
        *,
        environment: Mapping[str, str | Path] | None = None,
        capture_output: bool = True,
    ) -> None:
        if not _WINETRICKS_CMD.exists():
            raise BatoceraException(f'{_WINETRICKS_CMD} is missing, winetricks is not installed')

        environment = dict(environment or {})

        # the installer of a redist wants a display, which an ssh login has none of
        if not any(environment.get(name) or os.environ.get(name) for name in ('DISPLAY', 'WAYLAND_DISPLAY')):
            display = local_display()
            _logger.debug('no display in the environment, using %s', display)
            environment.update(display)

        self.run_in_prefix([_WINETRICKS_CMD, *arguments], environment=environment, capture_output=capture_output)

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
        users = self.prefix_dir / 'drive_c' / 'users'

        if not users.is_dir():
            return

        # only the ones wine linked, it ships either Music or My Music, not both
        for user in users.iterdir():
            for name in (
                'Downloads',
                'Documents',
                'My Documents',
                'Music',
                'My Music',
                'Pictures',
                'My Pictures',
                'Videos',
                'My Videos',
                'Templates',
            ):
                directory = user / name

                if directory.is_symlink():
                    directory.unlink()
                    directory.mkdir(parents=True, exist_ok=True)
                    _logger.debug('sandboxed %s', directory)

    def __list_files_from_user_dir(self, name: str, suffixes: Iterable[str], /) -> list[Path]:
        """
        The files the user dropped in /userdata/system/wine/<name> for the prefix to
        take in. They are moved to installed.<name> once they have been, so that they
        are only imported once.
        """
        source_dir = USER_WINE_DIR / name

        if not source_dir.is_dir():
            return []

        wanted = {suffix.lower() for suffix in suffixes}
        files = sorted(file for file in source_dir.iterdir() if file.is_file() and file.suffix.lower() in wanted)

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
            log.write(f'{datetime.now():%D %T} - Installed: {file} --> {self.prefix_dir}\n')

        _logger.debug('imported %s into %s', file, self.prefix_dir)

    def install_redists(self, /) -> None:
        """Run the redistributables the user dropped in /userdata/system/wine/exe."""
        for installer in self.__list_files_from_user_dir('exe', ['.exe']):
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
        for package in self.__list_files_from_user_dir('msi', ['.msi']):
            _logger.info('installing %s', package)
            self.run_in_prefix([self.msiexec, '-i', package, '/quiet', '/qn', '/norestart'])
            self.__imported(package, 'msi')

    def install_regs(self, /) -> None:
        """Import the registry files the user dropped in /userdata/system/wine/regs."""
        for registry in self.__list_files_from_user_dir('regs', ['.reg']):
            _logger.info('importing %s', registry)
            self.regedit(registry)
            self.__imported(registry, 'regs')

    def install_fonts(self, /) -> None:
        """Add the fonts the user dropped in /userdata/system/wine/fonts to the prefix,
        and the ones the runner ships, as ge-proton does."""
        fonts_dir = self.prefix_dir / 'drive_c' / 'windows' / 'Fonts'

        for font in self.__list_files_from_user_dir('fonts', ['.ttf', '.ttc']):
            fonts_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(font, fonts_dir / font.name)
            self.__imported(font, 'fonts')

        runner_fonts = self.__wine_path / 'share' / 'fonts'

        if not runner_fonts.is_dir():
            return

        # copied rather than linked, the prefix outlives the runner it was built with
        for font in sorted(runner_fonts.glob('*.tt[fc]')):
            target = fonts_dir / font.name

            # a font of its own is left alone, whoever put it there
            if target.is_file() and not target.is_symlink():
                continue

            fonts_dir.mkdir(parents=True, exist_ok=True)

            # a prefix from before this was copied still links into the runner
            if target.is_symlink():
                target.unlink()

            shutil.copy(font, target)

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
            registry = (self.prefix_dir / 'system.reg').read_text(encoding='utf-8', errors='replace')
        except OSError:
            registry = ''

        # writing it costs a wine start, so only do it when it isn't already set
        if wanted in registry:
            return

        self.set_registry_value(
            r'HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\winebus',
            'DisableHidraw',
            'REG_DWORD',
            '0' if enabled else '1',
        )

    def get_environment(self, /) -> dict[str, str | Path]:
        return {
            **self.__wine_environment(),
            # so that the game finds the wineserver and the tools of its own runner
            'PATH': f'{self.wineserver.parent}:{os.environ.get("PATH", "/bin:/usr/bin")}',
        }

    @classmethod
    def default(cls, bottle_name: str, /) -> Self:
        return cls(_DEFAULT_WINE_RUNNER, bottle_name)

    @classmethod
    def from_prefix(cls, name: str | None, prefix: Path, /, *, arch: str | None = None) -> Self:
        """
        A runner for a prefix given as a path rather than named as a bottle: a rom that
        is a prefix itself, or a prefix that is about to be built somewhere of its own.
        """
        return cls(name or _DEFAULT_WINE_RUNNER, prefix=prefix, arch=arch)
