from __future__ import annotations

import logging
import os
import subprocess
from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final, Literal, Self

from ..batoceraPaths import HOME

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

_logger = logging.getLogger(__name__)

WINE_BASE: Final = Path('/usr/wine')

_WINETRICKS: Final = WINE_BASE / 'winetricks'
_WINE_BOTTLES: Final = HOME / 'wine-bottles'

type RunnerNames = Literal['wine-tkg', 'wine-proton']
_DEFAULT_WINE_RUNNER: Final[RunnerNames] = 'wine-tkg'


@dataclass
class Runner:
    name: InitVar[RunnerNames]
    bottle_name: InitVar[str]

    bottle_dir: Path = field(init=False)
    wine: Path = field(init=False)
    wine64: Path = field(init=False)

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
            env_path = f'{wine_server_bin}:/bin:/usr/bin'
        else:
            wine_bin = wine_lib / 'i386-unix'
            wine64_bin = wine_lib / 'x86_64-unix'
            wine = wine_bin / 'wine'
            wine64 = wine64_bin / 'wine64'
            env_path = f'{wine_bin}:{wine64_bin}:{wine_server_bin}:/bin:/usr/bin'

        self.wine = wine
        self.wine64 = wine64
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
