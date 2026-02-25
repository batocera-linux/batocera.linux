from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from batocera_common.asyncio import run

if TYPE_CHECKING:
    from pathlib import Path

_logger = logging.getLogger(__name__)


# a game that was killed rather than closed leaves processes holding the mount while they
# die, so a busy mount is worth waiting on rather than giving up on straight away
async def unmount(mount_point: Path, /, *, attempts: int = 10, delay: float = 0.5) -> bool:
    last_error: str | None = None

    for attempt in range(attempts):
        result = await run('umount', mount_point, text=True)

        if result.returncode == 0:
            return True

        last_error = result.stderr.strip()

        if not attempt:
            _logger.debug("'%s' is busy, waiting for it to be released", mount_point)

        await asyncio.sleep(delay)

    # detach it anyway, the kernel drops it once the last process lets go: leaving it
    # mounted would keep the rom busy until the next reboot
    _logger.warning("'%s' is still busy, detaching it lazily because %s", mount_point, last_error or 'unknown error')

    return (await run('umount', '-l', mount_point)).returncode == 0
