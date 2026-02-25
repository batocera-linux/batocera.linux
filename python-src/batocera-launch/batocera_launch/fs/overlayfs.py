from __future__ import annotations

import logging
import shutil
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from batocera_common.paths import ROM_OVERLAY_DIR

from ..exceptions import BatoceraException
from .mounts import mount, unmount

if TYPE_CHECKING:
    from _typeshed import StrPath
    from collections.abc import AsyncGenerator
    from pathlib import Path


_logger = logging.getLogger(__name__)


async def _unmount_and_remove(mount_point: Path, /) -> None:
    if mount_point.is_mount() and not await unmount(mount_point):
        _logger.error("failed unmounting '%s'", mount_point)

        # Skip the follow-on removal if the umount failed because it might still
        # be connected to the ROM's save area (system crashing or bad state?).
        return

    shutil.rmtree(mount_point, ignore_errors=True)


def _escape_value(value: StrPath, /, *, include_colons: bool = False) -> str:
    """Escape a value for use in an overlayfs mount option string."""

    result = str(value).replace('\\', '\\\\').replace(',', r'\,')

    if include_colons:
        return result.replace(':', r'\:')

    return result


async def _mount(read_only_dir: Path, writable_upper_dir: Path, writable_work_dir: Path, mount_point: Path, /) -> bool:
    components = ','.join(
        (
            f'lowerdir={_escape_value(read_only_dir, include_colons=True)}',
            f'upperdir={_escape_value(writable_upper_dir)}',
            f'workdir={_escape_value(writable_work_dir)}',
        )
    )

    try:
        await mount('overlay', mount_point, 'overlay', data=components)
    except Exception:
        _logger.exception("failed mounting '%s' with components '%s'", mount_point, components)

        return False

    _logger.debug("mounted '%s' with components '%s'", mount_point, components)

    return True


@asynccontextmanager
async def mount_overlayfs(read_only_dir: Path, writable_dir: Path, /) -> AsyncGenerator[Path]:
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
    """

    # If we were passed a single file, then overlay its parent directory
    maybe_rom_file = None
    if read_only_dir.is_file():
        _logger.debug("overlaying single-file or linked rom '%s'", read_only_dir)
        maybe_rom_file = read_only_dir.name
        read_only_dir = read_only_dir.parent

    # Where overlayfs keeps persistent writes
    writable_upper_dir = writable_dir / 'upper'
    writable_upper_dir.mkdir(parents=True, exist_ok=True)

    # Where overlayfs manages in-flight writes
    writable_work_dir = writable_dir / 'work'
    writable_work_dir.mkdir(parents=True, exist_ok=True)

    # Where overlayfs exposes the combined filesystem
    mount_point = ROM_OVERLAY_DIR / read_only_dir.name
    await _unmount_and_remove(mount_point)
    mount_point.mkdir(parents=True, exist_ok=True)

    if not await _mount(read_only_dir, writable_upper_dir, writable_work_dir, mount_point):
        raise BatoceraException(f"Unable to setup writable overlay for '{read_only_dir}'")
    try:
        yield (mount_point / maybe_rom_file) if maybe_rom_file else mount_point

    finally:
        _logger.debug("cleaning up '%s'", mount_point)
        await _unmount_and_remove(mount_point)

        has_writes = writable_upper_dir.is_dir() and any(writable_upper_dir.iterdir())

        _logger.debug("%s save directory '%s'", 'keeping populated' if has_writes else 'removing empty', writable_dir)

        if not has_writes:
            shutil.rmtree(writable_dir, ignore_errors=True)
