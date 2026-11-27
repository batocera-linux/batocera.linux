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

import json
import logging
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final, cast

from .devfreq import boost, restore, should_boost
from .key_value_config import KeyValueConfig
from .paths import BATOCERA_CONF
from .settings import settings_sections
from .sysfs import read_sysfs, write_sysfs

if TYPE_CHECKING:
    from collections.abc import Callable, Container, Iterable, Mapping

_logger: Final = logging.getLogger(__name__)

CPU_DIR: Final = Path('/sys/devices/system/cpu')
CPUFREQ_DIR: Final = CPU_DIR / 'cpufreq'
POWER_SUPPLY_DIR: Final = Path('/sys/class/power_supply')
RUNNING_GAME_URL: Final = 'http://127.0.0.1:1234/runningGame'
# control center changes to the running game
GAME_CHANGES: Final = Path('/var/run/batocera-perf.changes')

POWER_MODES: Final = frozenset(('highperformance', 'balanced', 'conservative', 'powersaver'))

_BALANCED_GOVERNORS: Final = ('schedutil', 'ondemand', 'conservative', 'powersave')
_CONSERVATIVE_GOVERNORS: Final = ('conservative', *_BALANCED_GOVERNORS)
_DEFAULT_EPP: Final = ('default', 'performance')
_CONSERVATIVE_EPP: Final = ('balance_power', *_DEFAULT_EPP)


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


def power_mode(value: str | None, /) -> str | None:
    return value if value in POWER_MODES else None


def global_power_mode(settings: Mapping[str, str], /, *, connected: bool | None = None) -> str:
    if connected is None:
        connected = is_power_connected()

    if connected:
        return power_mode(settings.get('powermode')) or 'balanced'

    return power_mode(settings.get('batterymode')) or 'conservative'


def apply_power_mode(mode: str, /) -> None:
    if not cpufreq_available():
        return

    match mode:
        case 'highperformance':
            set_governor('performance')
            _set_first_available(('performance',), available_epp(), set_epp)
        case 'balanced':
            _set_first_available(_BALANCED_GOVERNORS, available_governors(), set_governor)
            _set_first_available(_DEFAULT_EPP, available_epp(), set_epp)
        case 'conservative':
            _set_first_available(_CONSERVATIVE_GOVERNORS, available_governors(), set_governor)
            _set_first_available(_CONSERVATIVE_EPP, available_epp(), set_epp)
        case 'powersaver':
            set_governor('powersave')
            _set_first_available(('power',), available_epp(), set_epp)
        case _:
            _logger.warning('unknown power mode %r', mode)


def is_power_connected() -> bool:
    """Trust a charger's online flag when the board has one, else the battery's own status; no battery means mains."""
    # controllers and mice report their own batteries with a Device scope
    supplies = [supply for supply in POWER_SUPPLY_DIR.glob('*') if read_sysfs(supply / 'scope') != 'Device']
    batteries = [supply for supply in supplies if read_sysfs(supply / 'type') == 'Battery']
    chargers = [online for supply in supplies if supply not in batteries and (online := read_sysfs(supply / 'online'))]

    if chargers:
        return '1' in chargers

    return all(read_sysfs(battery / 'status') != 'Discharging' for battery in batteries)


@dataclass(frozen=True, slots=True)
class RunningGame:
    system: str
    rom: Path


def running_game() -> RunningGame | None:
    try:
        with urllib.request.urlopen(RUNNING_GAME_URL, timeout=1) as response:
            game = json.load(response)
    except OSError, ValueError:
        return None

    if not isinstance(game, dict):
        return None

    game = cast('dict[str, object]', game)
    system, path = game.get('systemName'), game.get('path')

    if not isinstance(system, str) or not isinstance(path, str) or not system or not path:
        return None

    return RunningGame(system, Path(path))


def _changed_mode(game: RunningGame, /) -> str | None:
    try:
        changes = dict(line.split('=', 1) for line in GAME_CHANGES.read_text().splitlines() if '=' in line)
    except OSError:
        return None

    return power_mode(changes.get('mode')) if changes.get('game') == str(game.rom) else None


def current_power_mode(
    game: RunningGame | None, /, *, connected: bool | None = None, user_config: KeyValueConfig | None = None
) -> str:
    if user_config is None:
        user_config = KeyValueConfig(BATOCERA_CONF)

    if game is not None:
        if (mode := _changed_mode(game)) is not None:
            return mode

        for section in settings_sections(game.system, game.rom):
            if (mode := power_mode(user_config.section(section).get('powermode'))) is not None:
                return mode

    return global_power_mode(user_config.section('global'), connected=connected)


def apply_current_power_mode(*, connected: bool | None = None) -> None:
    game = running_game()
    mode = current_power_mode(game, connected=connected)
    apply_power_mode(mode)

    if game is not None:
        if should_boost(mode):
            boost()
        else:
            restore()


_SOURCES: Final = {'ac': True, 'battery': False, 'auto': None}


def main() -> None:
    args = [arg.lower() for arg in sys.argv[1:]]

    match args:
        case []:
            apply_current_power_mode()
        case ['auto' | 'ac' | 'battery' as source]:
            apply_current_power_mode(connected=_SOURCES[source])
        case ['get']:
            print(current_power_mode(running_game()))
        case ['get', 'ac' | 'battery' as source]:
            print(global_power_mode(KeyValueConfig(BATOCERA_CONF).section('global'), connected=_SOURCES[source]))
        case [mode] if mode in POWER_MODES:
            apply_power_mode(mode)
        case _:
            print(
                f'Usage: {sys.argv[0]} [auto|ac|battery|get [ac|battery]|highperformance|balanced|conservative|powersaver]',
                file=sys.stderr,
            )
            sys.exit(1)
