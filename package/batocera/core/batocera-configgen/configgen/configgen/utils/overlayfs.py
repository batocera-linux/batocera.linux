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


def _mount(read_only_dir: Path, writable_upper_dir: Path, writable_work_dir: Path, mount_point: Path) -> bool:

    components = f"lowerdir={read_only_dir},upperdir={writable_upper_dir},workdir={writable_work_dir}"

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
def mount_overlayfs(read_only_dir: Path, writable_dir: Path, /) -> Iterator[Path]:
    """
    The Linux kernel's overlay file system (overlayfs) creates a virtual file
    system mount point based on a "stack" of two or more of underlying directory
    trees where the lower directories get occluded (or overridden by)
    directories higher up the stack.

    Three things to note:

    - Changes are only written to the top-most directory or the 'upper'
      directory, in overlayfs jargon, while the 'lower' directories are
      effectively read-only.

    - Overlayfs operates at the logical file level as opposed to operating at
      the block-level, so it's perfectly fine (and normal) to mix file systems,
      such as a squashfs mount point being used as the read-only lower layer and
      some writable directory (coming from ext4 or even tmpfs) as the writable
      layer.

    - Overlayfs requires the writable directory be split into 'upper' and 'work'
      subdirectories. The 'work' directory is where in-flight changes accumulate
      before being atomically moved into the public 'upper' area. You'll see
      these "upper" and "work" sub-directories being created off the passed in
      "writable_dir" in the code below. This is a requirement of overlayfs and
      essentially internal workings. They must both exist on the same file
      system for the atomic moves to work properly.

    The main use-case in batocera will be supporting writes on top of a
    read-only underlying directory tree of files, specifically for emulators
    that take in a tree of files like DOS, Wine, Amiga, and probably others. To
    this end, this function takes in the read-only directory as well as the
    target writable directory, and returns the mount point of the overlay file
    system.

    Typically the read-only directory will be a ROM's squashfs mount point, and
    the writable directory will be the ROM's 'saves' path, while the returned
    mount-point will be /var/run/overlays/<...> (named after the ROM).

    This also means the user is free to manage their saved changes: they can
    delete them to reset the state of the game or they can back them up, etc.

    This is coded as a context, so when the context closes (due to clean exit or
    exception), the overlay will be unmounted.
    """

    # If we were passed a single file, then overlay its parent directory
    maybe_rom_file = None
    if read_only_dir.is_file():
        _logger.debug("overlaying single-file or linked rom '%s'", read_only_dir)
        maybe_rom_file = read_only_dir.name
        read_only_dir  = read_only_dir.parent

    # Where overlayfs keeps persistent writes
    writable_upper_dir = writable_dir / "upper"
    mkdir_if_not_exists(writable_upper_dir)

    # Where overlayfs manages in-flight writes
    writable_work_dir = writable_dir / "work"
    mkdir_if_not_exists(writable_work_dir)

    # Where overlayfs exposes the combined filesystem
    mount_point = _OVERLAY_BASE_DIR / read_only_dir.name
    _unmount_and_remove(mount_point)
    mkdir_if_not_exists(mount_point)

    if not _mount(read_only_dir, writable_upper_dir, writable_work_dir, mount_point):
        raise BatoceraException(f"Unable to setup writable overlay for '{read_only_dir}'")
    try:
        yield mount_point / maybe_rom_file if maybe_rom_file else mount_point

    finally:
        _logger.debug("cleaning up '%s'", mount_point)
        _unmount_and_remove(mount_point)

        has_writes = writable_upper_dir.is_dir() and any(writable_upper_dir.iterdir())

        _logger.debug("%s save directory '%s'",
                      "keeping populated" if has_writes else "removing empty",
                      writable_dir)

        if not has_writes:
            shutil.rmtree(writable_dir, ignore_errors=True)
