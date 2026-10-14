from __future__ import annotations

import logging
import sys
import time
from pathlib import Path
from typing import Final

from .power import read_sysfs, write_sysfs

_logger: Final = logging.getLogger(__name__)

PLATFORM_PROFILE_DIR: Final = Path('/sys/class/platform-profile')

# the firmware applies a profile's power limits about a second after the switch
PROFILE_SETTLE_SECONDS: Final = 2

_HIGHEST_POWER: Final = ('custom', 'max-power', 'performance')


def _handlers() -> list[Path]:
    return sorted(PLATFORM_PROFILE_DIR.glob('platform-profile-*'))


def _choices(handler: Path, /) -> frozenset[str]:
    return frozenset((read_sysfs(handler / 'choices') or '').split())


def available_platform_profiles() -> frozenset[str]:
    return frozenset[str]().union(*(_choices(handler) for handler in _handlers()))


def current_platform_profile() -> str | None:
    for handler in _handlers():
        return read_sysfs(handler / 'profile')

    return None


def set_platform_profile(profile: str, /) -> bool:
    """Set the profile on every handler offering it and return whether anything changed."""
    changed = False

    for handler in _handlers():
        if profile not in _choices(handler) or read_sysfs(handler / 'profile') == profile:
            continue

        # the class interface, unlike /sys/firmware/acpi/platform_profile, accepts custom
        write_sysfs(handler / 'profile', profile)
        changed = changed or read_sysfs(handler / 'profile') == profile

    if not changed:
        _logger.debug('platform profile %s not applied', profile)

    return changed


def set_highest_power_profile() -> bool:
    choices = available_platform_profiles()

    for profile in _HIGHEST_POWER:
        if profile in choices:
            return set_platform_profile(profile)

    return False


def main() -> None:
    match sys.argv[1:]:
        case ['get']:
            print(current_platform_profile() or '')
        case ['list']:
            print(' '.join(sorted(available_platform_profiles())))
        case ['max']:
            # print the previous profile so the caller can put it back
            print(current_platform_profile() or '')

            if set_highest_power_profile():
                time.sleep(PROFILE_SETTLE_SECONDS)
        case ['set', profile]:
            if set_platform_profile(profile):
                time.sleep(PROFILE_SETTLE_SECONDS)
        case _:
            print(f'Usage: {sys.argv[0]} get|list|max|set <profile>', file=sys.stderr)
            sys.exit(1)
