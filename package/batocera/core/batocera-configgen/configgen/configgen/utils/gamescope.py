from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from ..exceptions import BatoceraException

if TYPE_CHECKING:
    from ..Command import Command
    from ..Emulator import Emulator
    from ..types import Resolution

_logger = logging.getLogger(__name__)

def is_GBM_Supported() -> bool:
    try:
        eglinfo_bin = Path("/usr/bin/eglinfo")
        if not eglinfo_bin.exists():
            return False

        eglCmd = '/usr/bin/eglinfo | grep EGL_KHR_platform_gbm'
        eglCmdResult = subprocess.run(eglCmd, shell=True, capture_output=True, text=True)
        grep_return_code = eglCmdResult.returncode

        return grep_return_code == 0

    except Exception:
        return False

def add_gamescope_arguments(command: Command, system: Emulator, CurrentResolution: Resolution, /) -> None:

    if not system.config.get_bool("gamescope"):
        return

    if not is_GBM_Supported():
        raise BatoceraException("GPU driver don't support gamescope")

    gamescope_arguments = ["/usr/bin/gamescope"]

    # Retrieve output resolution from system options.
    # if not defined, inherit from the current screen resolution
    output_resolution = system.config.get_str("gamescope_output_resolution")
    if output_resolution:
        output_width, _, output_height = output_resolution.partition("x")
    else:
        output_width = f'{CurrentResolution["width"]}'
        output_height = f'{CurrentResolution["height"]}'

    gamescope_arguments.extend([
        "-W", output_width.strip(),
        "-H", output_height.strip()
    ])

    # Retrieve nested resolution from system options.
    # default undefined inherit from gamescopt_output_resoluton
    # the nested_resolution is upscaled|downscaled to output_resolution

    nested_resolution = system.config.get_str("gamescope_nested_resolution")
    if nested_resolution:
        nested_width, _, nested_height = nested_resolution.partition("x")
        gamescope_arguments.extend([
            "-w", nested_width.strip(),
            "-h", nested_height.strip()
        ])

    # Retrieve nested refresh rate.
    # Default is undefined with output refresh forced to 60hz
    # if nested refresh is defined, output refresh is equal to nested refresh
    nested_refresh = system.config.get_str("gamescope_nested_refresh")
    if nested_refresh:
        gamescope_arguments.extend(["-r", str(nested_refresh)])

    # Framerate limit, used by gamescope as a divisor of the refresh rate.
    framerate_limit = system.config.get_str("gamescope_framerate_limit")
    if framerate_limit:
        gamescope_arguments.extend(["--framerate-limit", framerate_limit])

    # Upscaler type.
    # default is stretched if undefined
    scaler = system.config.get_str("gamescope_scaler")
    if scaler:
        gamescope_arguments.extend(["-S", scaler])

    # Upscaler filter.
    # default is linear if undefined
    upscale_filter = system.config.get_str("gamescope_filter")
    if upscale_filter:
        gamescope_arguments.extend(["-F", upscale_filter])

    # Upscaler sharpness
    sharpness = system.config.get_str("gamescope_sharpness")
    if sharpness:
        gamescope_arguments.extend(["--sharpness", sharpness])

    if system.config.get_bool("gamescope_hdr"):
        sdr_gamut = system.config.get_str("gamescope_sdr_gamut_wideness")
        if sdr_gamut:
            gamescope_arguments.extend(["--sdr-gamut-wideness", sdr_gamut])

        hdr_sdr_nits = system.config.get_str("gamescope_hdr_sdr_content_nits")
        if hdr_sdr_nits:
           gamescope_arguments.extend(["--hdr-sdr-content-nits", hdr_sdr_nits])

        if system.config.get_bool("gamescope_hdr_itm_enabled"):
           gamescope_arguments.append("--hdr-itm-enabled")

        hdr_itm_sdr_nits = system.config.get_str("gamescope_hdr_itm_sdr_nits")
        if hdr_itm_sdr_nits:
            gamescope_arguments.extend(["--hdr-itm-sdr-nits", hdr_itm_sdr_nits])

        hdr_itm_target = system.config.get_str("gamescope_hdr_itm_target_nits")
        if hdr_itm_target:
            gamescope_arguments.extend(["--hdr-itm-target-nits", hdr_itm_target])

    #expose native nested wayland to bypass Xwayland when possible
    if os.environ.get("WAYLAND_DISPLAY"):
        gamescope_arguments.append("--expose-wayland")

    #always fullscreen
    gamescope_arguments.append("-f")

    # Reshade effect.
    reshade_effect = system.config.get_str("gamescope_reshade_effect")
    if reshade_effect:
        gamescope_arguments.extend(["--reshade-effect", reshade_effect])

    gamescope_arguments.append("--")

    command.array = gamescope_arguments + command.array
