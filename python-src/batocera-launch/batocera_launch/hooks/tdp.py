from __future__ import annotations

import logging
import subprocess
from typing import TYPE_CHECKING, Final

from . import Hook

if TYPE_CHECKING:
    from ..config.config import SystemConfig

_logger: Final = logging.getLogger(__name__)

_AMD_TDP: Final = '/usr/bin/batocera-amd-tdp'


def tdp_watts(max_tdp: str, percentage: str, /) -> int | None:
    try:
        return round(float(max_tdp) * float(percentage) / 100)
    except ValueError:
        _logger.warning('invalid TDP value %r of %r', percentage, max_tdp)
        return None


def apply_tdp(watts: int, /) -> None:
    # ryzenadj is slow enough to matter; leave it to finish on its own
    subprocess.Popen(
        [_AMD_TDP, str(watts)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


class TdpHook(Hook):
    """Scale a supported AMD CPU's TDP by the configured percentage while a game runs."""

    _changed: bool = False

    def start(self, config: SystemConfig, /) -> None:
        # only set at boot when the CPU is supported
        max_tdp = config.user_config.get('system.cpu.tdp')

        if not max_tdp or (percentage := config.get_str('tdp')) is None:
            return

        if (watts := tdp_watts(max_tdp, percentage)) is not None:
            _logger.debug('setting TDP to %d W for %s', watts, config.rom.name)
            self._changed = True
            apply_tdp(watts)

    def stop(self, config: SystemConfig, /) -> None:
        if not self._changed:
            return

        max_tdp = config.user_config.get('system.cpu.tdp', '')
        percentage = config.global_settings.get('tdp')
        watts = tdp_watts(max_tdp, percentage if percentage is not None else '100')

        if watts is not None:
            _logger.debug('restoring TDP to %d W', watts)
            apply_tdp(watts)
