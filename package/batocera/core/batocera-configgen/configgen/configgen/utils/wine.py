from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

_logger = logging.getLogger(__name__)

WINE_BASE: Final = Path('/usr/wine')
DEFAULT_WINE_RUNNER: Final = 'wine-tkg'


def get_wine_paths(runner: str, /) -> dict[str, Path]:
    wine_path = WINE_BASE / runner
    wine_lib = wine_path / 'lib' / 'wine'
    wine_server_bin = wine_path / 'bin'

    if runner == 'wine-proton':
        wine_bin = wine_server_bin
        wine64_bin = wine_server_bin
        wine = wine_bin / 'wine'
        wine64 = wine64_bin / 'wine64'
    else:
        wine_bin = wine_lib / 'i386-unix'
        wine64_bin = wine_lib / 'x86_64-unix'
        wine = wine_bin / 'wine'
        wine64 = wine64_bin / 'wine64'

    return {
        'WINE_PATH': wine_path,
        'WINE_LIB': wine_lib,
        'WINE_BIN': wine_bin,
        'WINE64_BIN': wine64_bin,
        'WINE_SERVER_BIN': wine_server_bin,
        'WINE': wine,
        'WINE64': wine64,
        'WINETRICKS': WINE_BASE / 'winetricks',
    }

wine_paths = get_wine_paths(DEFAULT_WINE_RUNNER)
WINE_PATH, WINE_LIB, WINE_BIN, WINE64_BIN, WINE_SERVER_BIN, WINE, WINE64, WINETRICKS = (
    wine_paths['WINE_PATH'],
    wine_paths['WINE_LIB'],
    wine_paths['WINE_BIN'],
    wine_paths['WINE64_BIN'],
    wine_paths['WINE_SERVER_BIN'],
    wine_paths['WINE'],
    wine_paths['WINE64'],
    wine_paths['WINETRICKS'],
)


def _run_wine_process(
    prefix: Path,
    cmd: Sequence[str | Path],
    runner: str,
    /, *,
    environment: Mapping[str, str | Path] | None = None
) -> None:
    env = {
        'LD_LIBRARY_PATH': f'/lib32:{WINE_LIB}',
        'WINEPREFIX': prefix,
    }

    if environment:
        env.update(environment)

    env.update(os.environ)
    if runner == 'wine-proton':
        env['PATH'] = f'{WINE_SERVER_BIN}:/bin:/usr/bin'
    else:
        env['PATH'] = f'{WINE_BIN}:{WINE64_BIN}:{WINE_SERVER_BIN}:/bin:/usr/bin'

    _logger.debug('command: %s', cmd)

    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()

    _logger.debug(out.decode())
    _logger.error(err.decode())


def install_wine_trick(
    prefix: Path,
    name: str,
    /, *,
    environment: Mapping[str, str | Path] | None = None
) -> None:
    done_file = prefix / f'{name}.done'

    if done_file.exists():
        return

    _run_wine_process(prefix, [WINETRICKS, '-q', name], DEFAULT_WINE_RUNNER, environment=environment)

    done_file.write_text('done')


def regedit(prefix: Path, file: Path, /) -> None:
    _run_wine_process(prefix, [WINE, 'regedit', file], DEFAULT_WINE_RUNNER)


def get_wine_environment(prefix: Path, /) -> dict[str, str | Path]:
    return {
        'WINEPREFIX': prefix,
        'LD_LIBRARY_PATH': f'/lib32:{WINE_LIB}',
        'LIBGL_DRIVERS_PATH': '/lib32/dri',
        # hum pw 0.2 and 0.3 are hardcoded, not nice
        'SPA_PLUGIN_DIR': '/usr/lib/spa-0.2:/lib32/spa-0.2',
        'PIPEWIRE_MODULE_DIR': '/usr/lib/pipewire-0.3:/lib32/pipewire-0.3',
    }


def set_wine_runner(runner: str, /) -> None:
    global WINE_PATH, WINE_LIB, WINE_BIN, WINE64_BIN, WINE_SERVER_BIN, WINE, WINE64, WINETRICKS
    wine_paths = get_wine_paths(runner)
    WINE_PATH, WINE_LIB, WINE_BIN, WINE64_BIN, WINE_SERVER_BIN, WINE, WINE64, WINETRICKS = (
        wine_paths['WINE_PATH'],
        wine_paths['WINE_LIB'],
        wine_paths['WINE_BIN'],
        wine_paths['WINE64_BIN'],
        wine_paths['WINE_SERVER_BIN'],
        wine_paths['WINE'],
        wine_paths['WINE64'],
        wine_paths['WINETRICKS'],
    )

    _logger.debug('Updated wine paths for runner "%s":', runner)
    _logger.debug('WINE_PATH=%s', WINE_PATH)
    _logger.debug('WINE_LIB=%s', WINE_LIB)
    _logger.debug('WINE_BIN=%s', WINE_BIN)
    _logger.debug('WINE64_BIN=%s', WINE64_BIN)
    _logger.debug('WINE_SERVER_BIN=%s', WINE_SERVER_BIN)
    _logger.debug('WINE=%s', WINE)
    _logger.debug('WINE64=%s', WINE64)
