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
