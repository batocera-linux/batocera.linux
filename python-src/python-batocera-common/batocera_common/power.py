from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Final

from .settings import get_master_setting

if TYPE_CHECKING:
    from collections.abc import Callable, Container, Iterable

    from .key_value_config import KeyValueConfig

_logger: Final = logging.getLogger(__name__)

CPU_DIR: Final = Path('/sys/devices/system/cpu')
CPUFREQ_DIR: Final = CPU_DIR / 'cpufreq'
POWER_SUPPLY_DIR: Final = Path('/sys/class/power_supply')

POWER_MODES: Final = frozenset(('highperformance', 'balanced', 'powersaver'))

_BALANCED_GOVERNORS: Final = ('schedutil', 'ondemand', 'conservative', 'powersave')
_DEFAULT_EPP: Final = ('default', 'performance')


def read_sysfs(path: Path, /) -> str | None:
    try:
        return path.read_text().strip()
    except OSError:
        return None


def write_sysfs(path: Path, value: str, /) -> None:
    try:
        path.write_text(value)
    except OSError:
        _logger.debug('cannot write %s to %s', value, path)


def _words(path: Path, /) -> frozenset[str]:
    return frozenset((read_sysfs(path) or '').split())


def cpufreq_available() -> bool:
    policy = CPUFREQ_DIR / 'policy0'

    return (policy / 'scaling_governor').exists() and (policy / 'scaling_available_governors').exists()


def available_governors() -> frozenset[str]:
    return _words(CPUFREQ_DIR / 'policy0' / 'scaling_available_governors')


def set_governor(governor: str, /) -> None:
    for path in CPUFREQ_DIR.glob('policy*/scaling_governor'):
        if read_sysfs(path) != governor:
            write_sysfs(path, governor)


def available_epp() -> frozenset[str]:
    return _words(CPU_DIR / 'cpu0' / 'cpufreq' / 'energy_performance_available_preferences')


def set_epp(preference: str, /) -> None:
    for path in CPU_DIR.glob('cpu*/cpufreq/energy_performance_preference'):
        write_sysfs(path, preference)


def _set_first_available(
    candidates: Iterable[str], available: Container[str], setter: Callable[[str], None], /
) -> None:
    for candidate in candidates:
        if candidate in available:
            setter(candidate)
            return


def apply_default(*, user_config: KeyValueConfig | None = None) -> None:
    governor = get_master_setting('system.cpu.governor', user_config=user_config)

    if governor is not None and governor in available_governors():
        set_governor(governor)
        _set_first_available(_DEFAULT_EPP, available_epp(), set_epp)


def apply_power_mode(mode: str | None, /, *, user_config: KeyValueConfig | None = None) -> None:
    if not cpufreq_available():
        return

    match mode:
        case None | 'default':
            apply_default(user_config=user_config)
        case 'highperformance':
            set_governor('performance')
            _set_first_available(('performance',), available_epp(), set_epp)
        case 'balanced':
            _set_first_available(_BALANCED_GOVERNORS, available_governors(), set_governor)
            _set_first_available(_DEFAULT_EPP, available_epp(), set_epp)
        case 'powersaver':
            set_governor('powersave')
            _set_first_available(('power',), available_epp(), set_epp)
        case _:
            _logger.warning('unknown power mode %r', mode)


def is_power_connected() -> bool:
    """Trust a charger's online flag when the board has one, else the battery's own status; no battery means mains."""
    supplies = list(POWER_SUPPLY_DIR.glob('*'))
    batteries = [supply for supply in supplies if read_sysfs(supply / 'type') == 'Battery']
    chargers = [online for supply in supplies if supply not in batteries and (online := read_sysfs(supply / 'online'))]

    if chargers:
        return '1' in chargers

    return all(read_sysfs(battery / 'status') != 'Discharging' for battery in batteries)


def main() -> None:
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else ''

    match mode:
        case 'ac':
            apply_power_mode(get_master_setting('global.powermode'))
        case 'battery':
            apply_power_mode(get_master_setting('global.batterymode') or 'balanced')
        case 'default' | 'highperformance' | 'balanced' | 'powersaver':
            apply_power_mode(mode)
        case _:
            print(f'Usage: {sys.argv[0]} [ac|battery|default|highperformance|balanced|powersaver]', file=sys.stderr)
            sys.exit(1)
