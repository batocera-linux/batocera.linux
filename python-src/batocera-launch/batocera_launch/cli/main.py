from __future__ import annotations

from typing import Final

from ..logging import setup_logging
from ..profiler import Profiler
from .arguments import Arguments

_MAX_PLAYERS: Final = 8


def main() -> None:
    arguments = Arguments.parse(_MAX_PLAYERS)

    with setup_logging(), Profiler('/var/run/batocera-launch.perf') as profiler:
        from ..launch import launch

        launch(arguments, profiler)


if __name__ == '__main__':
    main()
