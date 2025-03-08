from __future__ import annotations

import os
from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator
    from cProfile import Profile

# 1) touch /var/run/emulatorlauncher.perf
# 2) start a game
# 3) gprof2dot.py -f pstats -n 5 /var/run/emulatorlauncher.prof -o emulatorlauncher.dot # wget https://raw.githubusercontent.com/jrfonseca/gprof2dot/master/gprof2dot.py
# 4) dot -Tpng emulatorlauncher.dot -o emulatorlauncher.png
# 3) or upload the file /var/run/emulatorlauncher.prof on https://nejc.saje.info/pstats-viewer.html

_profile: Profile | None = None


if os.path.exists('/var/run/emulatorlauncher.perf'):  # noqa: PTH110
    import cProfile

    _profile = cProfile.Profile()


def start() -> None:
    if _profile:
        _profile.enable()


def stop() -> None:
    if _profile:
        _profile.disable()
        _profile.dump_stats('/var/run/emulatorlauncher.prof')


@contextmanager
def pause() -> Iterator[None]:
    if not _profile:
        yield
        return

    _profile.disable()
    yield
    _profile.enable()
