# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Final

from .types import Resolution

if TYPE_CHECKING:
    from .config.config import Config

_logger: Final = logging.getLogger(__name__)

_GAMESCOPE_BIN: Final = Path('/usr/bin/gamescope')


def gamescope_available() -> bool:
    # only the nested Wayland backend is built, so it needs a labwc session
    return _GAMESCOPE_BIN.exists() and bool(os.environ.get('WAYLAND_DISPLAY'))


def game_resolution(config: Config, output: Resolution, /) -> Resolution:
    if value := config.get_str('gamescope_resolution'):
        width, _, height = value.partition('x')
        try:
            return Resolution(width=int(width), height=int(height))
        except ValueError:
            _logger.warning('Invalid gamescope resolution: %s', value)

    return output


def gamescope_args(config: Config, output: Resolution, /, *, expose_wayland: bool = False) -> list[str]:
    game = game_resolution(config, output)
    args = [
        str(_GAMESCOPE_BIN),
        '-W',
        str(output.width),
        '-H',
        str(output.height),
        '-w',
        str(game.width),
        '-h',
        str(game.height),
    ]

    if scaler := config.get_str('gamescope_scaler'):
        args += ['-S', scaler]

    if upscale_filter := config.get_str('gamescope_filter'):
        args += ['-F', upscale_filter]

    if sharpness := config.get_str('gamescope_sharpness'):
        args += ['--sharpness', sharpness]

    if fps_limit := config.get_str('gamescope_fps_limit'):
        args += ['--framerate-limit', fps_limit]

    if config.get_bool('display.hdr'):
        args.append('--hdr-enabled')

    if expose_wayland:
        args.append('--expose-wayland')

    return [*args, '-f', '--']
