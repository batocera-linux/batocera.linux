from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Final

from batocera_common.asyncio import run

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

_logger: Final = logging.getLogger(__name__)


async def set_mouse_mode(mode: bool, /) -> None:
    _logger.debug('change_mouse_mode(%s)', mode)
    await run('batocera-mouse', 'show' if mode else 'hide', shell=True)


@asynccontextmanager
async def prepare_mouse(mode: bool, /) -> AsyncGenerator[None]:
    if mode:
        await set_mouse_mode(True)

    try:
        yield
    finally:
        if mode:
            try:
                await set_mouse_mode(False)
            except Exception:
                pass
