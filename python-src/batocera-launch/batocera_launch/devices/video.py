from __future__ import annotations

import asyncio
import logging
import re
import subprocess
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final

from batocera_common.asyncio import run

from ..exceptions import BatoceraException
from ..types import Resolution, ScreenInfo

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from ..config.config import SystemConfig

_logger: Final = logging.getLogger(__name__)
_ROTATION_FILE: Final = Path('/var/run/rk-rotation')
_GLXINFO_BIN: Final = Path('/usr/bin/glxinfo')


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


async def list_outputs(*, timeout: float | None = None) -> list[str]:
    try:
        coro = run('batocera-resolution', 'listOutputs', shell=True, text=True, check=True)

        if timeout is not None:
            coro = asyncio.wait_for(coro, timeout=timeout)

        proc = await coro
    except Exception:
        _logger.exception('Failed to check display count')
        return []

    return proc.stdout.split()


async def get_current_output() -> str:
    proc = await run('batocera-resolution', 'currentOutput', shell=True, text=True)
    return proc.stdout.strip()


async def supports_system_rotation() -> bool:
    proc = await run('batocera-resolution', 'supportSystemRotation', shell=True, text=True)
    return proc.returncode == 0


async def get_screen_info(config: SystemConfig, /) -> list[ScreenInfo]:
    outputs = await list_outputs()
    infos: list[ScreenInfo] = []

    # output 1
    output_1 = await get_current_output()
    resolution_1 = await get_current_resolution()
    infos.append(ScreenInfo(resolution_1, 0, 0))

    # output 2
    output_2: str | None = None

    # find the configured one
    if (
        (output_2_config := config.get_str('videooutput2'))
        and output_2_config in outputs
        and output_2_config != output_1
    ):
        output_2 = output_2_config

    # find the first one
    if output_2 is None:
        for output in outputs:
            if output != output_1:
                output_2 = output
                break

    resolution_2: Resolution | None = None
    if output_2 is not None:
        try:
            resolution_2 = await get_current_resolution(output_2)
            infos.append(ScreenInfo(resolution_2, resolution_1.width, 0))
        except Exception:
            pass  # ignore bad information

    # output 3
    output_3 = None

    # find the configured one
    if (
        (output_3_config := config.get('videooutput3'))
        and output_3_config in outputs
        and output_3_config not in (output_1, output_2)
    ):
        output_3 = output_3_config

    # find the first one
    if output_3 is None:
        for output in outputs:
            if output not in (output_1, output_2):
                output_3 = output
                break

    if output_3 is not None:
        try:
            resolution_3 = await get_current_resolution(output_3)
            infos.append(
                ScreenInfo(
                    resolution_3,
                    # if resolution_2 can't be determined, place screen 3 where screen 2 would be
                    resolution_1.width + (0 if resolution_2 is None else resolution_2.width),
                    0,
                )
            )
        except Exception:
            pass  # ignore bad information

    _logger.debug('Screens: %s', infos)

    return infos


@dataclass(slots=True, frozen=True)
class GLInfo:
    vendor: str
    version: float


_OPENGL_VENDOR_RE: Final = re.compile(r'^OpenGL vendor string: (?P<vendor>.*)$')
_OPENGL_VERSION_RE: Final = re.compile(r'^OpenGL version string: (?P<version>\d+\.\d+)\b')


async def get_gl_info() -> GLInfo:
    vendor = 'unknown'
    version = 0

    if _GLXINFO_BIN.exists():
        try:
            proc = await run('glxinfo -B', text=True, check=True)

            for line in proc.stdout.splitlines():
                if match := _OPENGL_VENDOR_RE.match(line):
                    vendor = match.group('vendor').strip().casefold()
                if match := _OPENGL_VERSION_RE.match(line):
                    version_str = match.group('version').strip()
                    version = float(version_str)
        except Exception:
            pass

    return GLInfo(vendor=vendor, version=version)


@asynccontextmanager
async def prepare_resolution(wanted_mode: str, /) -> AsyncGenerator[Resolution]:
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
