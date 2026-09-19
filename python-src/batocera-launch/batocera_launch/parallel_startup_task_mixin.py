from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import field
from typing import TYPE_CHECKING, Self

from batocera_common.dataclasses import cached_dataclass

from .emulator import Emulator

if TYPE_CHECKING:
    from types import TracebackType

    from .command import Command


@cached_dataclass
class ParallelStartupTaskMixin(Emulator, ABC):
    _parallel_startup_task: asyncio.Task[None] = field(init=False)

    @abstractmethod
    async def parallel_startup_task(self) -> None: ...

    async def before_run(self, command: Command, /) -> None:
        # Make sure the startup task is awaited as late as possible
        await super().before_run(command)
        # Wait for the parallel startup task to complete before running the command
        await self._parallel_startup_task

    async def __aenter__(self) -> Self:
        self._parallel_startup_task = asyncio.create_task(self.parallel_startup_task())

        try:
            return await super().__aenter__()
        except BaseException:
            # Cancel the task if the context manager fails to enter (e.g. KeyboardInterrupt)
            self._parallel_startup_task.cancel()
            try:
                # await the task and suppress the CancelledError to ensure aiohttp cleanup happens
                await self._parallel_startup_task
            except asyncio.CancelledError:
                pass

            raise

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> bool | None:
        # Cancel the task if the context manager exits
        self._parallel_startup_task.cancel()

        try:
            # await the task and suppress the CancelledError to ensure aiohttp cleanup happens
            await self._parallel_startup_task
        except asyncio.CancelledError:
            pass

        return await super().__aexit__(exc_type, exc_value, traceback)
