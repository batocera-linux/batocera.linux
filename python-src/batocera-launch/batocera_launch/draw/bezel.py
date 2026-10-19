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
