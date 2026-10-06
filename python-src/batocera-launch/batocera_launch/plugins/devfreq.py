from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final

from batocera_common.power import read_sysfs, write_sysfs
from batocera_common.settings import get_master_setting

from ..plugin_manager import HookContext, Plugin
from .power import resolve_power_mode

if TYPE_CHECKING:
    from batocera_common.key_value_config import KeyValueConfig

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


def should_boost(mode: str | None, /, *, user_config: KeyValueConfig | None = None) -> bool:
    if mode is not None:
        return mode == 'highperformance'

    return get_master_setting('system.cpu.governor', user_config=user_config) == 'performance'


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


def _restore(path: Path, /) -> None:
    state = _state_file(path)

    if (previous := read_sysfs(state)) is not None:
        write_sysfs(path, previous)
        state.unlink(missing_ok=True)


class DevfreqPlugin(Plugin):
    def start(self, context: HookContext, /) -> None:
        knobs = detect_knobs()

        if not knobs:
            return

        boost = should_boost(resolve_power_mode(context.config), user_config=context.config.user_config)

        for path, knob in knobs:
            # left behind by a launch that never reached stop
            _restore(path)

            if boost and (current := read_sysfs(path)) is not None and current != knob.boost and _save(path, current):
                write_sysfs(path, knob.boost)

    def stop(self, context: HookContext, /) -> None:
        for path, _ in detect_knobs():
            _restore(path)
