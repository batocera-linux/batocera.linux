from __future__ import annotations

import logging
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

_OVERLAY_BASE_DIR: Final = Path("/var/run/overlays/")


def _unmount_and_remove(mount_point: Path):
    if mount_point.is_mount():
        result = subprocess.run(["umount", str(mount_point)], capture_output=True, text=True)
        if result.returncode != 0:
            _logger.error("failed unmounting '%s' (rc=%d) because %s",
                          mount_point, result.returncode, result.stderr.strip())

            # Skip the follow-on removal if the umount failed because it might still
            # be connected to the ROM's save area (system crashing or bad state?).
            return

    shutil.rmtree(mount_point, ignore_errors=True)


def _mount(lower: Path, upper: Path, work: Path, mount_point: Path) -> bool:
    components = f"lowerdir={lower},upperdir={upper},workdir={work}"

    result = subprocess.run(["mount", "-t", "overlay", "overlay",
                             "-o", components, str(mount_point)],
                             capture_output=True, text=True)

    if result.returncode == 0:
        _logger.debug("mounted '%s' with components '%s'",
                       mount_point, components)
    else:
        _logger.error("failed mounting '%s' with components '%s' (rc=%d) because %s",
                      mount_point, components, result.returncode, result.stderr.strip())

    return result.returncode == 0


@contextmanager
def mount_overlayfs(lower_dir: Path, writes_dir: Path, /) -> Iterator[Path]:
    """
    Create an overlay mount for a read-only lower directory saving writes to the
    writes_dir. Returns the merged overlay mount point.
    """

    # If we were passed a single file, then overlay its parent directory
    lower_file = None
    if lower_dir.is_file():
        _logger.debug("overlaying single-file or linked rom '%s'", lower_dir)
        lower_dir  = lower_dir.parent
        lower_file = lower_dir.name

    # Where overlayfs keeps persistent writes
    upper_dir = writes_dir / "upper"
    mkdir_if_not_exists(upper_dir)

    # Where overlayfs manages in-flight writes
    work_dir = writes_dir / "work"
    mkdir_if_not_exists(work_dir)

    # Where overlayfs exposes the combined filesystem
    mount_point = _OVERLAY_BASE_DIR / lower_dir.name
    _unmount_and_remove(mount_point)
    mkdir_if_not_exists(mount_point)

    if not _mount(lower_dir, upper_dir, work_dir, mount_point):
        raise BatoceraException(f"Unable to setup writable overlay for '{lower_dir}'")
    try:
        yield mount_point / lower_file if lower_file else mount_point

    finally:
        _logger.debug("cleaning up '%s'", mount_point)
        _unmount_and_remove(mount_point)

        has_writes = upper_dir.is_dir() and any(upper_dir.iterdir())

        _logger.debug("%s save directory '%s'",
                      "keeping populated" if has_writes else "removing empty",
                      writes_dir)

        if not has_writes:
            shutil.rmtree(writes_dir, ignore_errors=True)
