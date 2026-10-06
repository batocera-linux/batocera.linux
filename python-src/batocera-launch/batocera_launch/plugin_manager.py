from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from importlib.metadata import entry_points
from typing import TYPE_CHECKING, Final, Literal

if TYPE_CHECKING:
    from .config.config import SystemConfig

_logger: Final = logging.getLogger(__name__)


type _HookName = Literal['start', 'stop']


@dataclass(frozen=True, slots=True)
class HookContext:
    config: SystemConfig


@dataclass(slots=True)
class Plugin:
    def start(self, context: HookContext, /) -> None:
        pass

    def stop(self, context: HookContext, /) -> None:
        pass


def _call_hook(plugin: Plugin, hook: _HookName, context: HookContext, /) -> None:
    try:
        getattr(plugin, hook)(context)
    except Exception:
        _logger.exception('%s failed on %s', type(plugin).__name__, hook)


@dataclass(slots=True)
class PluginManager:
    context: HookContext
    plugins: list[Plugin] = field(init=False)
    _started: list[asyncio.Task[None]] = field(init=False, default_factory=list[asyncio.Task[None]])

    def __post_init__(self) -> None:
        self.plugins = []

        for entry_point in entry_points(group='batocera_launch.plugins'):
            try:
                self.plugins.append(entry_point.load()())
            except Exception:
                _logger.exception('cannot load plugin %s', entry_point.name)

    def start(self) -> None:
        self._started = [
            asyncio.create_task(
                asyncio.to_thread(_call_hook, plugin, 'start', self.context),
                name=f'plugin-start-{plugin.__class__.__name__}',
            )
            for plugin in self.plugins
        ]

    async def ready(self) -> None:
        # shielded so a cancelled launch cannot cancel the start tasks before stop() waits on them
        await asyncio.shield(asyncio.gather(*self._started))

    async def stop(self) -> None:
        # also covers a launch that failed before ready()
        await self.ready()

        async with asyncio.TaskGroup() as group:
            for plugin in self.plugins:
                group.create_task(
                    asyncio.to_thread(_call_hook, plugin, 'stop', self.context),
                    name=f'plugin-stop-{plugin.__class__.__name__}',
                )
