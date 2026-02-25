from __future__ import annotations

import asyncio
import logging
import re
import subprocess
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Final

from batocera_common.asyncio import run
from batocera_launch.exceptions import BatoceraException
from batocera_launch.types import Resolution

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from batocera_launch.config.config import SystemConfig

_logger: Final = logging.getLogger(__name__)
_ROTATION_FILE: Final = Path('/var/run/rk-rotation')


async def get_current_mode() -> str:  # noqa: RET503
    proc = await run('batocera-resolution', 'currentMode', shell=True)

    for val in proc.stdout.decode().splitlines():
        return val  # return the first line

    if TYPE_CHECKING:
        raise AssertionError('unreachable')


async def min_to_max_resolution() -> None:
    await run('batocera-resolution', 'minToMaxResolution', shell=True)


_max_res_re: Final = re.compile(r'^max-[0-9]*x[0-9]*$')


async def mode_exists(video_mode: str) -> bool:
    # max resolution given
    if video_mode.startswith('max-'):
        matches = _max_res_re.match(video_mode)
        if matches is not None:
            return True

    # specific resolution given
    proc = await run('batocera-resolution', 'listModes', shell=True)
    for line in proc.stdout.decode().splitlines():
        values = line.split(':')
        if video_mode == values[0]:
            return True

    _logger.error('invalid video mode %s', video_mode)
    return False


async def change_mode(video_mode: str) -> None:
    if await mode_exists(video_mode):
        cmd = ['batocera-resolution', 'setMode', video_mode]
        _logger.debug('change_mode(%s): %s', video_mode, cmd)
        max_tries = 2  # maximum number of tries to set the mode
        for i in range(1, max_tries + 1):
            try:
                proc = await run(*cmd, text=True, check=True)
                _logger.debug(proc.stdout.strip())
                return
            except subprocess.CalledProcessError as e:
                _logger.error('Error setting video mode: %s', e.stderr)
                if i == max_tries - 1:
                    raise BatoceraException('Error setting video mode') from e
                await asyncio.sleep(1)


async def get_current_resolution(name: str | None = None) -> Resolution:
    if name is None:
        proc = await run('batocera-resolution', 'currentResolution', shell=True, text=True)
    else:
        proc = await run('batocera-resolution', f'--screen {name}', 'currentResolution', shell=True, text=True)

    vals = proc.stdout.split('x')
    return Resolution(width=int(vals[0]), height=int(vals[1]))


def is_resolution_reversed() -> bool:
    return _ROTATION_FILE.exists()


@asynccontextmanager
async def prepare_resolution(system_config: SystemConfig, /) -> AsyncGenerator[Resolution]:
    wanted_mode = system_config.video_mode
    system_mode = await get_current_mode()
    new_system_mode = system_mode
    resolution_changed = False

    if wanted_mode == '' or wanted_mode == 'default':
        _logger.debug('min_to_max_resolution')
        _logger.debug('video mode before minmax: %s', system_mode)
        await min_to_max_resolution()
        new_system_mode = await get_current_mode()
        if new_system_mode != system_mode:
            resolution_changed = True

    _logger.debug('current video mode: %s', new_system_mode)
    _logger.debug('wanted video mode: %s', wanted_mode)

    if wanted_mode != 'default' and wanted_mode != new_system_mode:
        await change_mode(wanted_mode)
        resolution_changed = True

    game_resolution = await get_current_resolution()

    if is_resolution_reversed():
        game_resolution = Resolution(width=game_resolution.height, height=game_resolution.width)

    _logger.debug('resolution: %sx%s', game_resolution.width, game_resolution.height)

    try:
        yield game_resolution
    finally:
        if resolution_changed:
            try:
                await change_mode(system_mode)
            except Exception:
                pass
