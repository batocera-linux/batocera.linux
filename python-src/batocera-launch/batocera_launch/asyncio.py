from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Final

from batocera_common.asyncio import run
from batocera_launch.paths import SYSTEM_SCRIPTS, USER_SCRIPTS

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Iterable
    from pathlib import Path

_logger: Final = logging.getLogger(__name__)


async def call_script(directory: Path, event: str, args: Iterable[str | Path], /) -> None:
    if not directory.is_dir():
        return

    for file in directory.iterdir():
        if file.is_dir():
            await call_script(file, event, args)
        elif os.access(file, os.X_OK):
            _logger.debug('calling script: %s', [file, event, *args])
            await run(file, *args)


@asynccontextmanager
async def script_caller(events: tuple[Iterable[str], Iterable[str]], /, *args: str | Path) -> AsyncGenerator[None]:
    before_events, after_events = events

    if isinstance(before_events, str):
        before_events = [before_events]

    if isinstance(after_events, str):
        after_events = [after_events]

    for event in before_events:
        for directory in (SYSTEM_SCRIPTS, USER_SCRIPTS):
            await call_script(directory, event, args)

    try:
        yield
    finally:
        for event in after_events:
            for directory in (USER_SCRIPTS, SYSTEM_SCRIPTS):
                await call_script(directory, event, args)
