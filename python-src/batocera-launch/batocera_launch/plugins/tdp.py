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
import subprocess
import time
from dataclasses import dataclass, field
from typing import Final

from batocera_common.platform_profile import PROFILE_SETTLE_SECONDS, current_platform_profile, set_platform_profile

from ..plugin_manager import HookContext, Plugin

_logger: Final = logging.getLogger(__name__)

_AMD_TDP: Final = '/usr/bin/batocera-amd-tdp'


def tdp_watts(max_tdp: str, percentage: str, /) -> int | None:
    try:
        return round(float(max_tdp) * float(percentage) / 100)
    except ValueError:
        _logger.warning('invalid TDP value %r of %r', percentage, max_tdp)
        return None


def apply_tdp(watts: int, /, *, detach: bool = False, delay: int = 0) -> None:
    command = [_AMD_TDP, str(watts)]

    if delay:
        command = ['sh', '-c', f'sleep {delay}; exec "$0" "$@"', *command]

    if not detach:
        # stop waits on this, and batocera-launch cannot exit until stop has run
        subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=10,
        )
        return

    # ryzenadj is slow enough to hold up the return to ES; leave it to finish on its own
    subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


@dataclass(slots=True)
class TdpPlugin(Plugin):
    """Set the platform profile, then scale a supported AMD CPU's TDP by the configured percentage while a game runs.

    Both live in one plugin because a profile change resets the firmware's power limits, so the TDP must follow it.
    """

    _changed: bool = field(init=False, default=False)
    _previous_profile: str | None = field(init=False, default=None)

    def start(self, context: HookContext, /) -> None:
        config = context.config
        profile_changed = False

        if (profile := config.get_str('platformprofile')) is not None:
            previous = current_platform_profile()

            if profile_changed := set_platform_profile(profile):
                _logger.debug('setting platform profile to %s for %s', profile, config.rom.name)
                self._previous_profile = previous

        # only set at boot when the CPU is supported
        max_tdp = config.user_config.get('system.cpu.tdp')

        if not max_tdp or (percentage := config.get_str('tdp')) is None:
            return

        if (watts := tdp_watts(max_tdp, percentage)) is not None:
            _logger.debug('setting TDP to %d W for %s', watts, config.rom.name)
            self._changed = True

            if profile_changed:
                time.sleep(PROFILE_SETTLE_SECONDS)

            apply_tdp(watts)

    def stop(self, context: HookContext, /) -> None:
        config = context.config
        restored = False

        if (profile := config.global_settings.get('platformprofile') or self._previous_profile) is not None:
            restored = set_platform_profile(profile)

        if not (self._changed or restored):
            return

        if not (max_tdp := config.user_config.get('system.cpu.tdp', '')):
            return

        percentage = config.global_settings.get('tdp')
        watts = tdp_watts(max_tdp, percentage if percentage is not None else '100')

        if watts is not None:
            _logger.debug('restoring TDP to %d W', watts)

            if restored:
                apply_tdp(watts, detach=True, delay=PROFILE_SETTLE_SECONDS)
            else:
                apply_tdp(watts, detach=True)
