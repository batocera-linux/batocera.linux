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

import time
from pathlib import Path
from typing import Final

from .settings import get_master_setting
from .sysfs import read_sysfs, write_sysfs

# picked by the control center or a game; exists while a fan daemon runs, which rereads it on every check
PROFILE_FILE: Final = Path('/var/run/batocera-fan.profile')

PROFILES: Final = ('quiet', 'balanced', 'performance', 'max')

# how far quiet moves each step of the curve later, and performance earlier
SHIFT_CELSIUS: Final = 10

# how often a daemon waiting for its next check looks for a new profile
PROFILE_POLL_SECONDS: Final = 0.5


def _profile(profile: str | None, /) -> str:
    # unknown ones, and default from before there were four, mean balanced
    return profile if profile in PROFILES else 'balanced'


def current_fan_profile() -> str:
    return _profile(read_sysfs(PROFILE_FILE))


def set_fan_profile(profile: str | None, /) -> None:
    """Switch the running fan daemon to a profile."""
    if PROFILE_FILE.exists():
        write_sysfs(PROFILE_FILE, _profile(profile))


def start_fan_profile() -> None:
    """For a fan daemon starting up: begin with the global profile."""
    PROFILE_FILE.write_text('')
    set_fan_profile(get_master_setting('global.fanprofile'))


def stop_fan_profile() -> None:
    PROFILE_FILE.unlink(missing_ok=True)


def wait_for_fan_check(profile: str, seconds: float, /) -> bool:
    """Wait for a daemon's next temperature check, cut short by a new profile, and return whether one came."""
    deadline = time.monotonic() + seconds

    while (left := deadline - time.monotonic()) > 0:
        time.sleep(min(PROFILE_POLL_SECONDS, left))

        if current_fan_profile() != profile:
            return True

    return False


def _shift(curve: list[str], celsius: int, /) -> list[str]:
    shifted: list[str] = []
    for step in curve:
        temperature, _, percent = step.partition('=')
        shifted.append(f'{min(max(float(temperature) + celsius, 0.0), 100.0):5.1f}={percent}')
    return shifted


def fan_curve(curve: list[str], profile: str, /) -> list[str]:
    """A daemon's "temperature=percent" curve, highest temperature first, for a profile."""
    match profile:
        case 'max':
            return ['0.0=100']
        case 'quiet':
            return _shift(curve, SHIFT_CELSIUS)
        case 'performance':
            return _shift(curve, -SHIFT_CELSIUS)
        case _:
            return curve
