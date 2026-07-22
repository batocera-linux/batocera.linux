from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from batocera_common.asyncio import run
from batocera_common.paths import SQUASHFS_DIR
from batocera_launch.exceptions import BatoceraException

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from pathlib import Path

_logger = logging.getLogger(__name__)


@asynccontextmanager
async def mount_squashfs(rom: Path, /) -> AsyncGenerator[Path]:
    _logger.debug('mount_squashfs(%s)', rom)
    mount_point = SQUASHFS_DIR / rom.stem

    SQUASHFS_DIR.mkdir(parents=True, exist_ok=True)

    # first, try to clean an empty remaining directory (for example because of a crash)
    if mount_point.exists() and mount_point.is_dir():
        _logger.debug('squashfs_rom: %s already exists', mount_point)
        # try to remove an empty directory, else, run the directory, ignoring the .squashfs
        try:
            mount_point.rmdir()
        except FileNotFoundError, OSError:
            _logger.debug('squashfs_rom: failed to rmdir %s', mount_point)
            yield mount_point
            # No cleanup is necessary
            return

    # ok, the base directory doesn't exist, let's create it and mount the squashfs on it
    mount_point.mkdir()

    proc = await run('mount', rom, mount_point)
    if proc.returncode:
        _logger.debug('squashfs_rom: mounting %s failed', mount_point)
        try:
            mount_point.rmdir()
        except FileNotFoundError, OSError:
            pass

        raise BatoceraException(f'Unable to mount the file {rom}')

    try:
        # if the squashfs contains a single file with the same name, take it as the rom file
        rom_single = mount_point / rom.stem
        if len(list(mount_point.iterdir())) == 1 and rom_single.exists():
            _logger.debug('squashfs: single rom %s', rom_single)
            yield rom_single
        else:
            try:
                rom_linked = (mount_point / '.ROM').resolve(strict=True)
            except OSError:
                yield mount_point
            else:
                _logger.debug('squashfs: linked rom %s', rom_linked)
                yield rom_linked
    finally:
        _logger.debug('mount_squashfs: cleaning up %s', mount_point)

        # unmount
        proc = await run('umount', mount_point)
        if proc.returncode:
            _logger.debug('mount_squashfs: unmounting %s failed', mount_point)
            raise BatoceraException(f'Unable to unmount the file {mount_point}')

        # cleaning the empty directory
        mount_point.rmdir()
