from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Final

from batocera_common.asyncio import run

from .exceptions import BatoceraException

if TYPE_CHECKING:
    from .command import Command
    from .config.config import Config
    from .types import Resolution

_logger: Final = logging.getLogger(__name__)

_GAMESCOPE_BIN: Final = Path('/usr/bin/gamescope')
_EGLINFO_BIN: Final = Path('/usr/bin/eglinfo')


async def is_gbm_supported() -> bool:
    if not _EGLINFO_BIN.exists():
        return False

    try:
        result = await run(_EGLINFO_BIN, text=True)
    except Exception:
        _logger.exception('Failed to run %s', _EGLINFO_BIN)
        return False

    return 'EGL_KHR_platform_gbm' in result.stdout


async def add_gamescope_arguments(command: Command, config: Config, resolution: Resolution, /) -> None:
    if not config.get_bool('gamescope'):
        return

    if not await is_gbm_supported():
        raise BatoceraException("GPU driver don't support gamescope")

    arguments: list[str] = [str(_GAMESCOPE_BIN)]

    # Retrieve output resolution from system options.
    # if not defined, inherit from the current screen resolution
    if output_resolution := config.get_str('gamescope_output_resolution'):
        output_width, _, output_height = output_resolution.partition('x')
    else:
        output_width = f'{resolution.width}'
        output_height = f'{resolution.height}'

    arguments.extend(['-W', output_width.strip(), '-H', output_height.strip()])

    # Retrieve nested resolution from system options.
    # default undefined inherit from gamescope_output_resolution
    # the nested_resolution is upscaled|downscaled to output_resolution
    if nested_resolution := config.get_str('gamescope_nested_resolution'):
        nested_width, _, nested_height = nested_resolution.partition('x')
        arguments.extend(['-w', nested_width.strip(), '-h', nested_height.strip()])

    # Retrieve nested refresh rate.
    # Default is undefined with output refresh forced to 60hz
    # if nested refresh is defined, output refresh is equal to nested refresh
    if nested_refresh := config.get_str('gamescope_nested_refresh'):
        arguments.extend(['-r', nested_refresh])

    # Framerate limit, used by gamescope as a divisor of the refresh rate.
    if framerate_limit := config.get_str('gamescope_framerate_limit'):
        arguments.extend(['--framerate-limit', framerate_limit])

    # Upscaler type.
    # default is stretched if undefined
    if scaler := config.get_str('gamescope_scaler'):
        arguments.extend(['-S', scaler])

    # Upscaler filter.
    # default is linear if undefined
    if upscale_filter := config.get_str('gamescope_filter'):
        arguments.extend(['-F', upscale_filter])

    # Upscaler sharpness
    if sharpness := config.get_str('gamescope_sharpness'):
        arguments.extend(['--sharpness', sharpness])

    if config.get_bool('gamescope_hdr'):
        if sdr_gamut := config.get_str('gamescope_sdr_gamut_wideness'):
            arguments.extend(['--sdr-gamut-wideness', sdr_gamut])

        if hdr_sdr_nits := config.get_str('gamescope_hdr_sdr_content_nits'):
            arguments.extend(['--hdr-sdr-content-nits', hdr_sdr_nits])

        if config.get_bool('gamescope_hdr_itm_enabled'):
            arguments.append('--hdr-itm-enabled')

        if hdr_itm_sdr_nits := config.get_str('gamescope_hdr_itm_sdr_nits'):
            arguments.extend(['--hdr-itm-sdr-nits', hdr_itm_sdr_nits])

        if hdr_itm_target := config.get_str('gamescope_hdr_itm_target_nits'):
            arguments.extend(['--hdr-itm-target-nits', hdr_itm_target])

    # expose native nested wayland to bypass Xwayland when possible
    if os.environ.get('WAYLAND_DISPLAY'):
        arguments.append('--expose-wayland')

    # always fullscreen
    arguments.append('-f')

    # Reshade effect.
    if reshade_effect := config.get_str('gamescope_reshade_effect'):
        arguments.extend(['--reshade-effect', reshade_effect])

    arguments.append('--')

    command.prepend_args(*arguments)
