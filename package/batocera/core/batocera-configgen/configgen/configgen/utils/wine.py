from __future__ import annotations

import logging
import os
import shutil
import subprocess
from dataclasses import InitVar, dataclass, field
from pathlib import Path, PureWindowsPath
from typing import TYPE_CHECKING, Final, Literal, Self

from ..batoceraPaths import HOME
from ..exceptions import BatoceraException

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

_logger = logging.getLogger(__name__)

WINE_BASE: Final = Path('/usr/wine')

_WINETRICKS: Final = WINE_BASE / 'winetricks'
_WINE_BOTTLES: Final = HOME / 'wine-bottles'
_BSOD: Final = Path('/usr/bin/bsod-wine')
_DXVK: Final = WINE_BASE / 'dxvk'
# a dxvk unpacked here replaces the shipped one, as it did for batocera-wine
_USER_DXVK: Final = HOME / 'wine' / 'dxvk'

# the windows directory each dxvk build belongs in
_DXVK_ARCHS: Final = (('x64', 'system32'), ('x32', 'syswow64'))

# $1 the wine binary, $2 the game, $3 the wineserver. the caller's environment carries
# WINEPREFIX. a rom on a squashfs is unmounted the moment this returns, so it may only
# return once nothing is left holding it, which is what batocera-wine's stopWineServer
# did: wine hands the game over to the wineserver and exits long before the game does,
# and a game that was killed rather than closed leaves wine processes behind that the
# wineserver won't reap. the game's own exit code stays the command's.
_RUN_GAME: Final = r'''
"$1" "$2"
status=$?

timeout 10 "$3" -w || "$3" -k

# whatever is still in this prefix is holding the rom: kill it and wait for it to go
for _ in 1 2 3 4 5 6 7 8 9 10; do
    holders=
    for entry in /proc/[0-9]*; do
        pid=${entry##*/}
        [ "$pid" = "$$" ] && continue
        grep -qz "WINEPREFIX=$WINEPREFIX" "$entry/environ" 2>/dev/null && holders="$holders $pid"
    done

    [ -z "$holders" ] && break

    kill -9 $holders 2>/dev/null
    sleep 0.2
done

exit "$status"
'''

type RunnerNames = Literal['wine-tkg', 'wine-proton']
_DEFAULT_WINE_RUNNER: Final[RunnerNames] = 'wine-tkg'

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

def get_game_exe(rom: Path, /) -> Path:
    # the rom names what to run in its autorun.cmd, we don't guess: a game is free to
    # rename its engine, and the other executables next to it are installers and tools
    autorun = rom / "autorun.cmd"

    if not (cmd := get_autorun_vars(rom).get('CMD')):
        raise BatoceraException(f"{autorun} doesn't exist or doesn't name the CMD to run")

    if not (exe := resolve_in_rom(get_game_dir(rom), cmd)).is_file():
        raise BatoceraException(f"The executable {cmd} named by {autorun} doesn't exist")

    _logger.debug("executable %s from autorun.cmd", exe)

    return exe


@dataclass
class Runner:
    name: InitVar[RunnerNames]
    bottle_name: InitVar[str]

    bottle_dir: Path = field(init=False)
    wine: Path = field(init=False)
    wine64: Path = field(init=False)
    wineserver: Path = field(init=False)

    __lib: Path = field(init=False)
    __env_path: str = field(init=False)

    def __post_init__(self, name: RunnerNames, bottle_name: str) -> None:
        wine_path = WINE_BASE / name
        wine_lib = wine_path / 'lib' / 'wine'
        wine_server_bin = wine_path / 'bin'

        if name == 'wine-proton':
            wine_bin = wine_server_bin
            wine64_bin = wine_server_bin
            wine = wine_bin / 'wine'
            wine64 = wine64_bin / 'wine64'

            # Fallback for Wine 11.10+ where wine64 does not exist
            if not wine64.exists():
                wine64 = wine

            env_path = f'{wine_server_bin}:/bin:/usr/bin'
        else:
            wine_bin = wine_lib / 'i386-unix'
            wine64_bin = wine_lib / 'x86_64-unix'
            wine = wine_bin / 'wine'
            wine64 = wine64_bin / 'wine64'

            # Fallback for Wine 11.10+ where wine64 does not exist
            if not wine64.exists():
                wine64 = wine
                env_path = f'{wine_bin}:{wine_server_bin}:/bin:/usr/bin'
            else:
                env_path = f'{wine_bin}:{wine64_bin}:{wine_server_bin}:/bin:/usr/bin'

        self.wine = wine
        self.wine64 = wine64
        self.wineserver = wine_server_bin / 'wineserver'
        self.bottle_dir = _WINE_BOTTLES / bottle_name
        self.__lib = wine_lib
        self.__env_path = env_path

    def __run_wine_process(
        self,
        cmd: Sequence[str | Path],
        /, *,
        environment: Mapping[str, str | Path] | None = None
    ) -> None:
        env = {
            'LD_LIBRARY_PATH': f'/lib32:{self.__lib}',
            'WINEPREFIX': self.bottle_dir,
        }

        if environment:
            env.update(environment)

        env.update(os.environ)
        env['PATH'] = self.__env_path

        _logger.debug('command: %s', cmd)

        proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()

        _logger.debug(out.decode())
        _logger.error(err.decode())

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
            self.__run_wine_process([self.wine, 'hostname'], environment={'WINEDLLOVERRIDES': 'winegstreamer='})
        finally:
            if splash is not None:
                splash.terminate()

        if not (self.bottle_dir / 'system.reg').exists():
            shutil.rmtree(self.bottle_dir, ignore_errors=True)
            raise BatoceraException(f'Failed initialising the wine prefix {self.bottle_dir}')

    def game_command(self, game_exe: Path, /) -> list[str | Path]:
        # the paths go in as arguments rather than inside the script, a rom directory
        # is free to have spaces in its name
        return ['/bin/sh', '-c', _RUN_GAME, 'wine-game', self.wine, game_exe, self.wineserver]

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

            target_dir = self.bottle_dir / 'drive_c' / 'windows' / windows_dir
            target_dir.mkdir(parents=True, exist_ok=True)

            for dll in sorted(source_dir.glob('*.dll')):
                link = target_dir / dll.name

                # wine puts its own builtin dll there when it bootstraps the prefix
                if link.is_symlink() or link.exists():
                    link.unlink()

                link.symlink_to(dll)
                overridden.add(dll.stem)

        if overridden:
            _logger.debug('dxvk: linked %s from %s into %s', ', '.join(sorted(overridden)), dxvk, self.bottle_dir)

        return overridden

    def install_wine_trick(
        self,
        name: str,
        /, *,
        environment: Mapping[str, str | Path] | None = None
    ) -> None:
        done_file = self.bottle_dir / f'{name}.done'

        if done_file.exists():
            return

        self.__run_wine_process([_WINETRICKS, '-q', name], environment=environment)

        done_file.write_text('done')

    def regedit(self, file: Path, /) -> None:
        self.__run_wine_process([self.wine, 'regedit', file])

    def get_environment(self, /) -> dict[str, str | Path]:
        return {
            'WINEPREFIX': self.bottle_dir,
            'LD_LIBRARY_PATH': f'/lib32:{self.__lib}',
            'LIBGL_DRIVERS_PATH': '/lib32/dri',
            # hum pw 0.2 and 0.3 are hardcoded, not nice
            'SPA_PLUGIN_DIR': '/usr/lib/spa-0.2:/lib32/spa-0.2',
            'PIPEWIRE_MODULE_DIR': '/usr/lib/pipewire-0.3:/lib32/pipewire-0.3',
        }

    @classmethod
    def default(cls, bottle_dir: str, /) -> Self:
        return cls(_DEFAULT_WINE_RUNNER, bottle_dir)
