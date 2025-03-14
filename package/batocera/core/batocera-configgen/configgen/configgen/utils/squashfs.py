from __future__ import annotations

import logging
import os
import shutil
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

def _squashfs_rom_cleanup(mount_point: Path, overlay: bool):
    _logger.debug("squashfs_rom: cleaning up %s", mount_point)

    if mount_point.is_mount():
        # umount rom
        return_code = subprocess.call(["umount", mount_point])
        if return_code != 0:
            _logger.debug("squashfs_rom: unmounting %s failed", mount_point)
            raise BatoceraException(f"Unable to unmount the file {mount_point}")
        mount_point.rmdir()

    if overlay:
        overlay_root = mount_point.parent
        mount_point_rw = overlay_root / "overlay"

        _logger.debug("squashfs_rom: cleaning up overlay root %s", overlay_root)

        if mount_point_rw.is_mount():
            # unmount overlay
            os.chdir(_SQUASHFS_DIR)
            return_code = subprocess.call(["umount", mount_point_rw])
            if return_code != 0:
                _logger.debug("squashfs_rom: unmounting %s failed", mount_point_rw)
                raise BatoceraException(f"Unable to unmount the file {mount_point_rw}")
        shutil.rmtree(overlay_root)

@contextmanager
def squashfs_rom(rom: Path, overlay: bool) -> Iterator[Path]:
    _logger.debug("squashfs_rom(%s)", rom)

    mkdir_if_not_exists(_SQUASHFS_DIR)

    if overlay:
        overlay_root   = _SQUASHFS_DIR / rom.stem
        mount_point    = overlay_root / "rom"
        overlay_delta  = overlay_root / "delta"
        overlay_tmp    = overlay_root / "tmp"
        mount_point_rw = overlay_root / "overlay"

        if overlay_root.exists() and overlay_root.is_dir():
            _logger.debug("squashfs_rom: %s overlay root already exists", overlay_root)
            _squashfs_rom_cleanup(mount_point, overlay)
    else:
        mount_point    = _SQUASHFS_DIR / rom.stem

        # first, try to clean an empty remaining directories (for example because of a crash)
        if mount_point.exists() and mount_point.is_dir():
            _logger.debug("squashfs_rom: %s already exists", mount_point)

            # try to remove an empty directory, else, run the directory, ignoring the .squashfs
            try:
                mount_point.rmdir()
            except (FileNotFoundError, OSError):
                _logger.debug("squashfs_rom: failed to rmdir %s", mount_point)
                yield mount_point
                # No cleanup is necessary
                return

    # ok, the base directory doesn't exist, let's create it and mount the squashfs on it
    mount_point.mkdir(parents=True)

    return_code = subprocess.call(["mount", rom, mount_point])
    if return_code != 0:
        _logger.debug("squashfs_rom: mounting %s failed", mount_point)
        try:
            mount_point.rmdir()
        except (FileNotFoundError, OSError):
            pass
        raise BatoceraException(f"Unable to mount the file {rom}")

    if overlay:
        for dir in [overlay_delta, overlay_tmp, mount_point_rw]: dir.mkdir(exist_ok=True)
        return_code = subprocess.call(["mount",
				       "-t", "overlay",
				       "overlay",
				       "-o", f"lowerdir={mount_point},upperdir={overlay_delta},workdir={overlay_tmp}",
				       mount_point_rw])
        if return_code != 0:
            _logger.debug("squashfs_rom: mounting overlay %s failed", mount_point_rw)
            _squashfs_rom_cleanup(mount_point, overlay)
            raise BatoceraException(f"Unable to mount the file {rom}")

    try:
        if overlay:
            working_mount_point = mount_point_rw
        else:
            working_mount_point = mount_point

        # if the squashfs contains a single file with the same name, take it as the rom file
        rom_single = working_mount_point / rom.stem
        if len(list(mount_point.iterdir())) == 1 and rom_single.exists():
            _logger.debug("squashfs: single rom %s", rom_single)
            yield rom_single
        else:
            try:
                rom_linked = (working_mount_point / ".ROM").resolve(strict=True)
            except OSError:
                yield working_mount_point
            else:
                _logger.debug("squashfs: linked rom %s", rom_linked)
                yield rom_linked
    finally:
        _squashfs_rom_cleanup(mount_point, overlay)
