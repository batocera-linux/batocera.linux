from __future__ import annotations

import logging
from contextlib import asynccontextmanager, suppress
from typing import TYPE_CHECKING

from batocera_common.asyncio import run
from batocera_common.paths import SQUASHFS_DIR
from batocera_launch.exceptions import BatoceraException
from batocera_launch.fs.mounts import unmount
from batocera_launch.fs.overlayfs import mount_overlayfs

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from pathlib import Path

_logger = logging.getLogger(__name__)


@asynccontextmanager
async def _mount_squashfs(rom: Path, /) -> AsyncGenerator[Path]:
    _logger.debug('mounting: %s', rom)
    mount_point = SQUASHFS_DIR / rom.stem

    SQUASHFS_DIR.mkdir(parents=True, exist_ok=True)

    # first, try to clean an empty remaining directory (for example because of a crash)
    if mount_point.exists() and mount_point.is_dir():
        _logger.debug('%s already exists', mount_point)

        # a previous run may have left the rom mounted here, after a crash or an unmount
        # that was refused: take it down rather than running the game off a stale mount,
        # which isn't necessarily even the same rom
        if mount_point.is_mount():
            _logger.debug('%s is still mounted, unmounting it first', mount_point)
            await unmount(mount_point)

        # whatever is left is not ours to run the game off: it isn't necessarily even
        # the same rom, and it would never be unmounted either
        try:
            mount_point.rmdir()
        except FileNotFoundError:
            pass
        except OSError as e:
            raise BatoceraException(f'Unable to clean the mount point {mount_point}') from e

    # ok, the base directory doesn't exist, let's create it and mount the squashfs on it
    mount_point.mkdir()

    proc = await run('mount', rom, mount_point)
    if proc.returncode:
        _logger.debug('mounting %s failed', mount_point)
        try:
            mount_point.rmdir()
        except FileNotFoundError, OSError:
            pass

        raise BatoceraException(f'Unable to mount the file {rom}')

    try:
        # if the squashfs contains a single file with the same name, take it as the rom file
        rom_single = mount_point / rom.stem
        if len(list(mount_point.iterdir())) == 1 and rom_single.exists():
            _logger.debug('single rom %s', rom_single)
            yield rom_single
        else:
            try:
                rom_linked = (mount_point / '.ROM').resolve(strict=True)
            except OSError:
                yield mount_point
            else:
                _logger.debug('linked rom %s', rom_linked)
                yield rom_linked
    finally:
        _logger.debug('cleaning up %s', mount_point)

        # unmount
        if not await unmount(mount_point):
            _logger.debug('unmounting %s failed', mount_point)
            raise BatoceraException(f'Unable to unmount the file {mount_point}')

        # cleaning the empty directory, a lazily detached mount may still hold it
        with suppress(OSError):
            mount_point.rmdir()


@asynccontextmanager
async def mount_squashfs(rom: Path, /, *, writable_dir: Path | None = None) -> AsyncGenerator[Path]:
    async with _mount_squashfs(rom) as mount_point:
        if writable_dir is None:
            yield mount_point
        else:
            async with mount_overlayfs(mount_point, writable_dir) as overlay_mount_point:
                yield overlay_mount_point
