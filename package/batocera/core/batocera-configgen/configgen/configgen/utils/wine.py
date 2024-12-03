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
WINE_PATH: Final = WINE_BASE / 'wine-tkg'
WINE_LIB: Final = WINE_PATH / 'lib' / 'wine'
WINE_BIN: Final = WINE_PATH / 'bin'
WINE: Final = WINE_BIN / 'wine'
WINE64: Final = WINE_BIN / 'wine64'
WINETRICKS: Final = WINE_BASE / 'winetricks'


def _run_wine_process(
    prefix: Path, cmd: Sequence[str | Path], /, *, environment: Mapping[str, str | Path] | None = None
) -> None:
    env = {
        'LD_LIBRARY_PATH': f'/lib32:{WINE_LIB}',
        'WINEPREFIX': prefix,
    }

    if environment:
        env.update(environment)

    env.update(os.environ)
    env['PATH'] = f'{WINE_BIN}:/bin:/usr/bin'

    _logger.debug('command: %s', cmd)

    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()

    _logger.debug(out.decode())
    _logger.error(err.decode())


def install_wine_trick(prefix: Path, name: str, /, *, environment: Mapping[str, str | Path] | None = None) -> None:
    done_file = prefix / f'{name}.done'

    if done_file.exists():
        return

    _run_wine_process(prefix, [WINETRICKS, '-q', name], environment=environment)

    done_file.write_text('done')


def regedit(prefix: Path, file: Path, /) -> None:
    _run_wine_process(prefix, [WINE, 'regedit', file])


def get_wine_environment(prefix: Path, /) -> dict[str, str | Path]:
    return {
        'WINEPREFIX': prefix,
        'LD_LIBRARY_PATH': f'/lib32:{WINE_LIB}',
        'LIBGL_DRIVERS_PATH': '/lib32/dri',
        # hum pw 0.2 and 0.3 are hardcoded, not nice
        'SPA_PLUGIN_DIR': '/usr/lib/spa-0.2:/lib32/spa-0.2',
        'PIPEWIRE_MODULE_DIR': '/usr/lib/pipewire-0.3:/lib32/pipewire-0.3',
    }
