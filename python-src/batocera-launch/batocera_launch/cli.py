from __future__ import annotations

from .profiler import Profiler


def main() -> None:
    with Profiler('/var/run/batocera-launch.perf') as profiler:
        from .launch import launch

        launch(profiler)


if __name__ == '__main__':
    main()
