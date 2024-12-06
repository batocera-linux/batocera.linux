from __future__ import annotations

import logging
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Final

from ..batoceraPaths import mkdir_if_not_exists

if TYPE_CHECKING:
    from collections.abc import Iterator

eslog = logging.getLogger(__name__)

_SQUASHFS_DIR: Final = Path("/var/run/squashfs/")


@contextmanager
def squashfs_rom(rom: str | Path, /) -> Iterator[str]:
    rom = Path(rom)

    eslog.debug(f"squashfs_rom({rom})")
    mount_point = _SQUASHFS_DIR / rom.stem

    mkdir_if_not_exists(_SQUASHFS_DIR)

    # first, try to clean an empty remaining directory (for example because of a crash)
    if mount_point.exists() and mount_point.is_dir():
        eslog.debug(f"squashfs_rom: {mount_point} already exists")
        # try to remove an empty directory, else, run the directory, ignoring the .squashfs
        try:
            mount_point.rmdir()
        except (FileNotFoundError, OSError):
            eslog.debug(f"squashfs_rom: failed to rmdir {mount_point}")
            yield str(mount_point)
            # No cleanup is necessary
            return

    # ok, the base directory doesn't exist, let's create it and mount the squashfs on it
    mount_point.mkdir()

    return_code = subprocess.call(["mount", rom, mount_point])
    if return_code != 0:
        eslog.debug(f"squashfs_rom: mounting {mount_point} failed")
        try:
            mount_point.rmdir()
        except (FileNotFoundError, OSError):
            pass
        raise Exception(f"unable to mount the file {rom}")

    try:
        # if the squashfs contains a single file with the same name, take it as the rom file
        rom_single = mount_point / rom.stem
        if len(list(mount_point.iterdir())) == 1 and rom_single.exists():
            eslog.debug(f"squashfs: single rom {rom_single}")
            yield str(rom_single)
        else:
            try:
                rom_linked = (mount_point / ".ROM").resolve(strict=True)
            except OSError:
                yield str(mount_point)
            else:
                eslog.debug(f"squashfs: linked rom {rom_linked}")
                yield str(rom_linked)
    finally:
        eslog.debug(f"squashfs_rom: cleaning up {mount_point}")

        # unmount
        return_code = subprocess.call(["umount", mount_point])
        if return_code != 0:
            eslog.debug(f"squashfs_rom: unmounting {mount_point} failed")
            raise Exception(f"unable to unmount the file {mount_point}")

        # cleaning the empty directory
        mount_point.rmdir()
