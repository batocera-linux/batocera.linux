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
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from .sysfs import read_sysfs, write_sysfs

_logger: Final = logging.getLogger(__name__)

STATE_DIR: Final = Path('/run/batocera-launch/devfreq')


@dataclass(frozen=True, slots=True)
class Knob:
    pattern: str
    boost: str
    governed: bool = True


KNOBS: Final = (
    Knob('sys/class/devfreq/*.gpu/governor', 'performance'),
    Knob('sys/class/devfreq/*dmc*/governor', 'performance'),
    Knob('sys/class/mpgpu/scale_mode', '2', governed=False),
)


def _available(path: Path, /) -> frozenset[str]:
    return frozenset((read_sysfs(path.with_name('available_governors')) or '').split())


def detect_knobs(knobs: tuple[Knob, ...] = KNOBS, /) -> list[tuple[Path, Knob]]:
    found: list[tuple[Path, Knob]] = []

    for knob in knobs:
        for path in sorted(Path('/').glob(knob.pattern)):
            if knob.governed and knob.boost not in _available(path):
                _logger.debug('%s has no %s governor', path, knob.boost)
                continue

            found.append((path, knob))

    return found


def should_boost(mode: str, /) -> bool:
    return mode == 'highperformance'


def _state_file(path: Path, /) -> Path:
    return STATE_DIR / '_'.join(path.parts[1:])


def _save(path: Path, value: str, /) -> bool:
    state = _state_file(path)

    try:
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(value)
    except OSError:
        _logger.warning('cannot save %s, leaving it alone', path)
        return False

    return True


def restore() -> None:
    for path, _ in detect_knobs():
        state = _state_file(path)

        if (previous := read_sysfs(state)) is not None:
            write_sysfs(path, previous)
            state.unlink(missing_ok=True)


def boost() -> None:
    for path, knob in detect_knobs():
        if _state_file(path).exists():
            continue

        if (current := read_sysfs(path)) is not None and current != knob.boost and _save(path, current):
            write_sysfs(path, knob.boost)
