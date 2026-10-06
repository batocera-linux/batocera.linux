from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager, suppress
from typing import TYPE_CHECKING

from batocera_common.fs import (
    MountFailedError,
    UnmountFailedError,
    manage_mount,
    unmount,
)
from batocera_common.paths import SQUASHFS_DIR

from ..exceptions import BatoceraException

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from pathlib import Path

_logger = logging.getLogger(__name__)


def _single_child_in_dir(directory: Path, /) -> Path | None:
    """Return the single child (file or directory) in a directory, or None if there isn't exactly one."""
    with os.scandir(directory) as entries:
        first = next(entries, None)

        if first is None or next(entries, None) is not None:
            return None

        return directory / first.name


@asynccontextmanager
async def mount_squashfs(rom: Path, /) -> AsyncGenerator[Path]:
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

            try:
                await unmount(mount_point)
            except Exception as e:
                raise BatoceraException(f'Unable to unmount the file {mount_point}') from e

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

    try:
        async with manage_mount(rom, mount_point) as mount_point:
            if (rom_single := _single_child_in_dir(mount_point)) is not None and rom_single.name == rom.stem:
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
    except MountFailedError as e:
        if e.mount_point == mount_point:
            _logger.exception('mounting %s failed', mount_point)

            try:
                mount_point.rmdir()
            except OSError:
                pass

            raise BatoceraException(f'Unable to mount the file {rom}') from e
        raise
    except UnmountFailedError as e:
        if e.mount_point == mount_point:
            _logger.debug('unmounting %s failed', mount_point)
            raise BatoceraException(f'Unable to unmount the file {mount_point}') from e
        raise
    finally:
        # cleaning the empty directory, a lazily detached mount may still hold it
        with suppress(OSError):
            mount_point.rmdir()
