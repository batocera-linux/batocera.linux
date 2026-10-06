from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass, field
from typing import Final

from ..plugin_manager import HookContext, Plugin

_logger: Final = logging.getLogger(__name__)

_AMD_TDP: Final = '/usr/bin/batocera-amd-tdp'


def tdp_watts(max_tdp: str, percentage: str, /) -> int | None:
    try:
        return round(float(max_tdp) * float(percentage) / 100)
    except ValueError:
        _logger.warning('invalid TDP value %r of %r', percentage, max_tdp)
        return None


def apply_tdp(watts: int, /, *, detach: bool = False) -> None:
    command = [_AMD_TDP, str(watts)]

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
    """Scale a supported AMD CPU's TDP by the configured percentage while a game runs."""

    _changed: bool = field(init=False, default=False)

    def start(self, context: HookContext, /) -> None:
        config = context.config

        # only set at boot when the CPU is supported
        max_tdp = config.user_config.get('system.cpu.tdp')

        if not max_tdp or (percentage := config.get_str('tdp')) is None:
            return

        if (watts := tdp_watts(max_tdp, percentage)) is not None:
            _logger.debug('setting TDP to %d W for %s', watts, config.rom.name)
            self._changed = True
            apply_tdp(watts)

    def stop(self, context: HookContext, /) -> None:
        if not self._changed:
            return

        config = context.config
        max_tdp = config.user_config.get('system.cpu.tdp', '')
        percentage = config.global_settings.get('tdp')
        watts = tdp_watts(max_tdp, percentage if percentage is not None else '100')

        if watts is not None:
            _logger.debug('restoring TDP to %d W', watts)
            apply_tdp(watts, detach=True)
