from __future__ import annotations

import contextlib
import logging
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Final

from ..batoceraPaths import mkdir_if_not_exists
from ..exceptions import BatoceraException
from .mounts import unmount

if TYPE_CHECKING:
    from collections.abc import Generator

_logger = logging.getLogger(__name__)

_SQUASHFS_DIR: Final = Path("/var/run/squashfs/")


@contextmanager
def mount_squashfs(rom: Path, /) -> Generator[Path]:
    _logger.debug("mount_squashfs(%s)", rom)
    mount_point = _SQUASHFS_DIR / rom.stem

    mkdir_if_not_exists(_SQUASHFS_DIR)

    # first, try to clean an empty remaining directory (for example because of a crash)
    if mount_point.exists() and mount_point.is_dir():
        _logger.debug("squashfs_rom: %s already exists", mount_point)

        # a previous run may have left the rom mounted here, after a crash or an unmount
        # that was refused: take it down rather than running the game off a stale mount,
        # which isn't necessarily even the same rom
        if mount_point.is_mount():
            _logger.debug("squashfs_rom: %s is still mounted, unmounting it first", mount_point)
            unmount(mount_point)

        # whatever is left is not ours to run the game off: it isn't necessarily even
        # the same rom, and it would never be unmounted either
        try:
            mount_point.rmdir()
        except FileNotFoundError:
            pass
        except OSError as e:
            raise BatoceraException(f"Unable to clean the mount point {mount_point}") from e

    # ok, the base directory doesn't exist, let's create it and mount the squashfs on it
    mount_point.mkdir()

    return_code = subprocess.call(["mount", rom, mount_point])
    if return_code != 0:
        _logger.debug("squashfs_rom: mounting %s failed", mount_point)
        try:
            mount_point.rmdir()
        except (FileNotFoundError, OSError):
            pass
        raise BatoceraException(f"Unable to mount the file {rom}")

    try:
        # if the squashfs contains a single file with the same name, take it as the rom file
        rom_single = mount_point / rom.stem
        if len(list(mount_point.iterdir())) == 1 and rom_single.exists():
            _logger.debug("squashfs: single rom %s", rom_single)
            yield rom_single
        else:
            try:
                rom_linked = (mount_point / ".ROM").resolve(strict=True)
            except OSError:
                yield mount_point
            else:
                _logger.debug("squashfs: linked rom %s", rom_linked)
                yield rom_linked
    finally:
        _logger.debug("mount_squashfs: cleaning up %s", mount_point)

        # unmount
        if not unmount(mount_point):
            _logger.debug("mount_squashfs: unmounting %s failed", mount_point)
            raise BatoceraException(f"Unable to unmount the file {mount_point}")

        # cleaning the empty directory, a lazily detached mount may still hold it
        with contextlib.suppress(OSError):
            mount_point.rmdir()
