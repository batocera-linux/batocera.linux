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
