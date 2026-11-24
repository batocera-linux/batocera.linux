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

from batocera_launch.config.config import Config
from batocera_launch.gamescope import game_resolution, gamescope_args
from batocera_launch.types import Resolution

_OUTPUT = Resolution(width=1920, height=1080)


def test_defaults_follow_the_output() -> None:
    assert gamescope_args(Config({}), _OUTPUT) == [
        '/usr/bin/gamescope',
        '-W',
        '1920',
        '-H',
        '1080',
        '-w',
        '1920',
        '-h',
        '1080',
        '-f',
        '--',
        'env',
        'WAYLAND_DISPLAY=none',
    ]


def test_options() -> None:
    config = Config(
        {
            'gamescope_resolution': '1024x768',
            'gamescope_scaler': 'fit',
            'gamescope_filter': 'fsr',
            'gamescope_sharpness': '5',
            'gamescope_fps_limit': '40',
            'display.hdr': '1',
        }
    )
    args = gamescope_args(config, _OUTPUT, expose_wayland=True)

    assert args[args.index('-w') + 1 : args.index('-h') + 2] == ['1024', '-h', '768']
    assert args[args.index('-S') + 1] == 'fit'
    assert args[args.index('-F') + 1] == 'fsr'
    assert args[args.index('--sharpness') + 1] == '5'
    assert args[args.index('--framerate-limit') + 1] == '40'
    assert '--hdr-enabled' in args
    assert '--expose-wayland' in args
    assert args[-2:] == ['-f', '--']


def test_invalid_resolution_falls_back_to_the_output() -> None:
    assert game_resolution(Config({'gamescope_resolution': 'bogus'}), _OUTPUT) == _OUTPUT
