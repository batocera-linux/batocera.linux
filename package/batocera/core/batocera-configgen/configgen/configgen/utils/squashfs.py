from __future__ import annotations

import logging
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Final

from ..batoceraPaths import mkdir_if_not_exists
from ..exceptions import BatoceraException

if TYPE_CHECKING:
    from collections.abc import Iterator

_logger = logging.getLogger(__name__)

_SQUASHFS_DIR: Final = Path("/var/run/squashfs/")


@contextmanager
def squashfs_rom(rom: str | Path, /) -> Iterator[str]:
    rom = Path(rom)

    _logger.debug("squashfs_rom(%s)", rom)
    mount_point = _SQUASHFS_DIR / rom.stem

    mkdir_if_not_exists(_SQUASHFS_DIR)

    # first, try to clean an empty remaining directory (for example because of a crash)
    if mount_point.exists() and mount_point.is_dir():
        _logger.debug("squashfs_rom: %s already exists", mount_point)
        # try to remove an empty directory, else, run the directory, ignoring the .squashfs
        try:
            mount_point.rmdir()
        except (FileNotFoundError, OSError):
            _logger.debug("squashfs_rom: failed to rmdir %s", mount_point)
            yield str(mount_point)
            # No cleanup is necessary
            return

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
            yield str(rom_single)
        else:
            try:
                rom_linked = (mount_point / ".ROM").resolve(strict=True)
            except OSError:
                yield str(mount_point)
            else:
                _logger.debug("squashfs: linked rom %s", rom_linked)
                yield str(rom_linked)
    finally:
        _logger.debug("squashfs_rom: cleaning up %s", mount_point)

        # unmount
        return_code = subprocess.call(["umount", mount_point])
        if return_code != 0:
            _logger.debug("squashfs_rom: unmounting %s failed", mount_point)
            raise BatoceraException(f"Unable to unmount the file {mount_point}")

        # cleaning the empty directory
        mount_point.rmdir()
