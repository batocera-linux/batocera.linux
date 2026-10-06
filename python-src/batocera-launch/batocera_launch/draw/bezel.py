from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Final

from batocera_common.paths import LOGS

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from pathlib import Path

    from ..types import Resolution

_logger = logging.getLogger(__name__)
_LOG_PATH: Final = LOGS / 'bezelOverlay.log'


@asynccontextmanager
async def bezel_overlay(bezel: Path | None, resolution: Resolution, /) -> AsyncGenerator[None]:
    overlay_proc: asyncio.subprocess.Process | None = None

    if bezel is not None and bezel.exists():
        _logger.info('Spawning standalone bezel overlay process for: %s', bezel)

        try:
            overlay_env = dict(os.environ)
            overlay_proc = await asyncio.create_subprocess_exec(
                '/usr/bin/batocera-bezel-overlay',
                '--log-level=debug',
                f'--log-file={_LOG_PATH}',
                bezel,
                str(resolution.width),
                str(resolution.height),
                env=overlay_env,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )

            # Give the window a moment to initialize and check if it crashed
            await asyncio.sleep(0.3)

            if overlay_proc.returncode is not None:
                _logger.error(
                    'Bezel overlay process exited immediately with status: %s. Check %s for details.',
                    overlay_proc.returncode,
                    _LOG_PATH,
                )
                overlay_proc = None
        except Exception:
            _logger.exception('Could not initialize standalone bezel overlay')

    try:
        yield
    finally:
        if overlay_proc is not None and overlay_proc.returncode is None:
            _logger.info('Terminating standalone bezel overlay process')

            overlay_proc.terminate()

            try:
                await asyncio.wait_for(overlay_proc.wait(), timeout=2)
            except TimeoutError:
                overlay_proc.kill()
