from __future__ import annotations

import asyncio
import logging
from subprocess import CalledProcessError
from typing import TYPE_CHECKING

from batocera_common.asyncio import run

if TYPE_CHECKING:
    from pathlib import Path

_logger = logging.getLogger(__name__)


# a game that was killed rather than closed leaves processes holding the mount while they
# die, so a busy mount is worth waiting on rather than giving up on straight away
async def unmount(mount_point: Path, /, *, attempts: int = 10, delay: float = 0.5) -> bool:
    for attempt in range(attempts):
        try:
            await run('umount', mount_point, text=True, check=True)

            return True
        except CalledProcessError as e:
            if e.returncode != 0 and 'busy' not in e.stderr:
                # No need to retry if the device isn't busy. Log it and return False.
                _logger.exception("Failed to unmount '%s' because %s", mount_point, e.stderr.strip())
                return False

        if not attempt:
            # Log on the first attempt only, to avoid spamming the logs
            _logger.debug("'%s' is busy, waiting for it to be released", mount_point)

        if attempt < attempts - 1:
            await asyncio.sleep(delay)

    _logger.warning("'%s' is still busy, detaching it lazily", mount_point)

    try:
        # detach it anyway, the kernel drops it once the last process lets go: leaving it
        # mounted would keep the rom busy until the next reboot
        await run('umount', '-l', mount_point, text=True, check=True)
    except CalledProcessError as e:
        _logger.exception("Failed to lazily detach '%s' because %s", mount_point, e.stderr.strip())
        return False

    return True
