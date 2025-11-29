from __future__ import annotations

import json
import logging
import subprocess
from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

    from ..generators.Generator import Generator

_logger = logging.getLogger(__name__)

@contextmanager
def set_gamescope_cmd(system: Emulator, CurrentResolution: Resolution, command: Command) -> Iterator[None]:

    if not system.config.get_bool("gamescope"):
        return

    gamescope_cmd = ["/usr/bin/gamescope"]

    # Retrieve output resolution from system options.
    # if not defined, inherit from the current screen resolution
    output_resolution = system.config.get_str("gamescope_output_resolution")
    if output_resolution:
        output_width, _, output_height = output_resolution.partition("x")
    else:
        output_width = str(CurrentResolution["width"])
        output_height = str(CurrentResolution["height"])

    gamescope_cmd.extend([
        "-W", output_width.strip(),
        "-H", output_height.strip()
    ])

    # Retrieve nested resolution from system options.
    # default undefined inherit from gamescopt_output_resoluton
    # the nested_resolution is upscaled|downscaled to output_resolution

    nested_resolution = system.config.get_str("gamescope_nested_resolution")
    if nested_resolution:
        nested_width, _, nested_height = nested_resolution.partition("x")
        gamescope_cmd.extend([
            "-w", nested_width.strip(),
            "-h", nested_height.strip()
        ])

    # Retrieve nested refresh rate.
    # Default 60 if undefined
    nested_refresh = system.config.get_str("gamescope_nested_refresh")
    if nested_refresh:
        gamescope_cmd.extend(["-r", str(nested_refresh)])

    # Upscaler type.
    # default is stretched if undefined
    scaler = system.config.get_str("gamescope_scaler")
    if scaler:
        gamescope_cmd.extend(["-S", scaler])

    # Upscaler filter.
    # default is linear if undefined
    filt = system.config.get_str("gamescope_filter")
    if filt:
        gamescope_cmd.extend(["-F", filt])

    # Upscaler sharpness
    sharpness = system.config.get_str("gamescope_sharpness")
    if sharpness:
        gamescope_cmd.extend(["--sharpness", sharpness])

    if system.config.get_bool("gamescope_hdr"):
        sdr_gamut = system.config.get_str("gamescope_sdr_gamut_wideness")
        if sdr_gamut:
            gamescope_cmd.extend(["--sdr-gamut-wideness", sdr_gamut])

        hdr_sdr_nits = system.config.get_str("gamescope_hdr_sdr_content_nits")
        if hdr_sdr_nits:
           gamescope_cmd.extend(["--hdr-sdr-content-nits", hdr_sdr_nits])

        if system.config.get_bool("gamescope_hdr_itm_enabled"):
           gamescope_cmd.append("--hdr-itm-enabled")

        hdr_itm_sdr_nits = system.config.get_str("gamescope_hdr_itm_sdr_nits")
        if hdr_itm_sdr_nits:
            gamescope_cmd.extend(["--hdr-itm-sdr-nits", hdr_itm_sdr_nits])

        hdr_itm_target = system.config.get_str("gamescope_hdr_itm_target_nits")
        if hdr_itm_target:
            gamescope_cmd.extend(["--hdr-itm-target-nits", hdr_itm_target])

    #always fullscreen
    gamescope_cmd.append("-f")

    # Reshade effect.
    reshade_effect = system.config.get_str("gamescope_reshade_effect")
    if reshade_effect:
        gamescope_cmd.extend(["--reshade-effect", reshade_effect])

    gamescope_cmd.append("--")

    command.array = gamescope_cmd + command.array
