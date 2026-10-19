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

import os
import sys
from typing import Final

from ..logging import setup_logging
from ..profiler import Profiler
from .arguments import Arguments

_MAX_PLAYERS: Final = 8


def main() -> None:
    arguments = Arguments.parse(_MAX_PLAYERS)

    try:
        with setup_logging(), Profiler('/var/run/batocera-launch.perf') as profiler:
            from ..launch import launch

            launch(arguments, profiler)
    except SystemExit as e:
        # ES waits for this process, and interpreter teardown is slow on small boards
        for stream in (sys.stdout, sys.stderr):
            if not stream.closed:
                stream.flush()
        os._exit(e.code if isinstance(e.code, int) else int(e.code is not None))


if __name__ == '__main__':
    main()
