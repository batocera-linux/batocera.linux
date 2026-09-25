from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final

from batocera_common.power import read_sysfs, write_sysfs
from batocera_common.settings import get_master_setting

from . import Hook
from .power import resolve_power_mode

if TYPE_CHECKING:
    from batocera_common.key_value_config import KeyValueConfig

    from ..config.config import SystemConfig

_logger: Final = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Knob:
    pattern: str
    boost: str
    # restore candidates when nothing was saved, first one the kernel offers wins
    idle: tuple[str, ...]
    governed: bool = True


KNOBS: Final = (
    Knob('sys/class/devfreq/*.gpu/governor', 'performance', ('simple_ondemand',)),
    Knob('sys/class/devfreq/*dmc*/governor', 'performance', ('dmc_ondemand', 'simple_ondemand')),
    Knob('sys/class/mpgpu/scale_mode', '2', ('1',), governed=False),
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


def idle_value(path: Path, knob: Knob, /) -> str:
    if knob.governed:
        available = _available(path)

        for candidate in knob.idle:
            if candidate in available:
                return candidate

    return knob.idle[0]


def should_boost(mode: str | None, /, *, user_config: KeyValueConfig | None = None) -> bool:
    if mode is not None:
        return mode == 'highperformance'

    return get_master_setting('system.cpu.governor', user_config=user_config) == 'performance'


class DevfreqHook(Hook):
    """Pin GPU and memory clocks for the game and put back whatever governor was there before."""

    def __init__(self) -> None:
        self._previous: dict[Path, str] = {}

    def start(self, config: SystemConfig, /) -> None:
        knobs = detect_knobs()

        if not knobs:
            return

        boost = should_boost(resolve_power_mode(config), user_config=config.user_config)

        for path, knob in knobs:
            current = read_sysfs(path)

            if boost:
                if current is not None and current != knob.boost:
                    self._previous[path] = current
                    write_sysfs(path, knob.boost)
            elif current == knob.boost:
                # left behind by a launch that never reached stop
                write_sysfs(path, idle_value(path, knob))

    def stop(self, config: SystemConfig, /) -> None:
        for path, knob in detect_knobs():
            if (previous := self._previous.get(path)) is not None:
                write_sysfs(path, previous)
            elif read_sysfs(path) == knob.boost:
                write_sysfs(path, idle_value(path, knob))
