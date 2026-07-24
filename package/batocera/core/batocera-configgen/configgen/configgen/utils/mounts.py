from __future__ import annotations

import logging
import subprocess
import time
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from pathlib import Path

_logger = logging.getLogger(__name__)

# a game that was killed rather than closed leaves processes holding the mount while they
# die, so a busy mount is worth waiting on rather than giving up on straight away
_UNMOUNT_ATTEMPTS: Final = 10
_UNMOUNT_DELAY: Final = 0.5


def unmount(mount_point: Path, /) -> bool:
    for attempt in range(_UNMOUNT_ATTEMPTS):
        result = subprocess.run(["umount", str(mount_point)], capture_output=True, text=True)

        if result.returncode == 0:
            return True

        if attempt == 0:
            _logger.debug("'%s' is busy, waiting for it to be released", mount_point)

        time.sleep(_UNMOUNT_DELAY)

    # detach it anyway, the kernel drops it once the last process lets go: leaving it
    # mounted would keep the rom busy until the next reboot
    _logger.warning("'%s' is still busy, detaching it lazily because %s",
                    mount_point, result.stderr.strip())

    return subprocess.run(["umount", "-l", str(mount_point)], capture_output=True, text=True).returncode == 0
