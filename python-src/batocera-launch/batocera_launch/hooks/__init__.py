from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final, Literal

if TYPE_CHECKING:
    from ..config.config import SystemConfig

_logger: Final = logging.getLogger(__name__)

type Event = Literal['start', 'stop']


class Hook:
    def start(self, config: SystemConfig, /) -> None:
        pass

    def stop(self, config: SystemConfig, /) -> None:
        pass


def _default_hooks() -> list[Hook]:
    from .devfreq import DevfreqHook
    from .mame import MameRotationHook
    from .power import PowerModeHook
    from .tdp import TdpHook

    return [PowerModeHook(), TdpHook(), DevfreqHook(), MameRotationHook()]


@dataclass(slots=True)
class Hooks:
    """Fires each hook in a worker thread and never waits; the interpreter joins them on exit."""

    config: SystemConfig
    hooks: list[Hook] = field(default_factory=_default_hooks)

    def start(self) -> None:
        self._fire('start')

    def stop(self) -> None:
        self._fire('stop')

    def _fire(self, event: Event, /) -> None:
        loop = asyncio.get_running_loop()

        for hook in self.hooks:
            loop.run_in_executor(None, _call, hook, event, self.config)


def _call(hook: Hook, event: Event, config: SystemConfig, /) -> None:
    try:
        if event == 'start':
            hook.start(config)
        else:
            hook.stop(config)
    except Exception:
        _logger.exception('%s failed on %s', type(hook).__name__, event)
