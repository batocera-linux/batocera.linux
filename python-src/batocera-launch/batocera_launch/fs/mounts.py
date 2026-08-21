from __future__ import annotations

import asyncio
import ctypes
import errno
import logging
import os
import sys
from enum import IntFlag
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

_logger = logging.getLogger(__name__)


if TYPE_CHECKING or sys.platform != 'linux':

    def _c_mount(source: bytes, target: bytes, fs_type: bytes, flags: int, data: bytes | None, /) -> int:
        raise NotImplementedError

    def _c_umount(target: bytes, /) -> int:
        raise NotImplementedError

    def _c_umount2(target: bytes, flags: int, /) -> int:
        raise NotImplementedError

else:
    _libc = ctypes.CDLL('libc.so.6', use_errno=True)

    _c_mount = _libc.mount
    _c_mount.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_ulong,
        ctypes.c_char_p,  # This is actually `const void *`, but all modern filesystems accept a string
    ]
    _c_mount.restype = ctypes.c_int

    _c_umount = _libc.umount
    _c_umount.argtypes = [ctypes.c_char_p]
    _c_umount.restype = ctypes.c_int

    _c_umount2 = _libc.umount2
    _c_umount2.argtypes = [
        ctypes.c_char_p,
        ctypes.c_int,
    ]
    _c_umount2.restype = ctypes.c_int


# From <linux/mount.h> (uapi/linux/mount.h)
class MountFlags(IntFlag):
    NONE = 0
    READONLY = 1
    NOSUID = 2
    NODEV = 4
    NOEXEC = 8
    SYNCHRONOUS = 16
    REMOUNT = 32
    MANDLOCK = 64
    DIRSYNC = 128
    NOSYMFOLLOW = 256
    NOATIME = 1024
    NODIRATIME = 2048
    BIND = 4096
    MOVE = 8192
    REC = 16384
    SILENT = 32768
    POSIXACL = 1 << 16
    UNBINDABLE = 1 << 17
    PRIVATE = 1 << 18
    SLAVE = 1 << 19
    SHARED = 1 << 20
    RELATIME = 1 << 21
    KERNMOUNT = 1 << 22
    I_VERSION = 1 << 23
    STRICTATIME = 1 << 24
    LAZYTIME = 1 << 25


def _ctype_caller[**P](
    func: Callable[P, int], os_error_filename: str | Path | None, /, *args: P.args, **kwargs: P.kwargs
) -> None:
    if func(*args, **kwargs) == -1:
        _errno = ctypes.get_errno()
        raise OSError(_errno, os.strerror(_errno), str(os_error_filename) if os_error_filename else None)


async def mount(
    source: str | Path, target: Path, fs_type: str, /, flags: MountFlags = MountFlags.NONE, data: str | None = None
) -> None:
    await asyncio.to_thread(
        _ctype_caller,
        _c_mount,
        target,
        os.fsencode(source),
        os.fsencode(target),
        fs_type.encode('utf-8'),
        int(flags),
        data if data is None else os.fsencode(data),
    )


async def _umount(target: Path, /, *, lazy: bool = False) -> None:
    if not lazy:
        await asyncio.to_thread(_ctype_caller, _c_umount, target, os.fsencode(target))
    else:
        await asyncio.to_thread(_ctype_caller, _c_umount2, target, os.fsencode(target), 2)  # 2 = MNT_DETACH


# a game that was killed rather than closed leaves processes holding the mount while they
# die, so a busy mount is worth waiting on rather than giving up on straight away
async def unmount(mount_point: Path, /, *, attempts: int = 10, delay: float = 0.5) -> bool:
    for attempt in range(attempts):
        try:
            await _umount(mount_point)

            return True
        except OSError as e:
            if e.errno != errno.EBUSY:
                # No need to retry if the error is not EBUSY. Log it and return False.
                _logger.exception("Failed to unmount '%s'", mount_point)
                return False

        if not attempt:
            # Log on the first attempt only, to avoid spamming the logs
            _logger.debug("'%s' is busy, waiting for it to be released", mount_point)

        if attempt < attempts - 1:
            await asyncio.sleep(delay)

    _logger.warning("'%s' is still busy, detaching it lazily", mount_point)

    try:
        # detach it anyway, the kernel drops it once the last process lets go: leaving it
        # mounted would keep the rom busy until the next reboot
        await _umount(mount_point, lazy=True)
    except OSError:
        _logger.exception("Failed to lazily detach '%s'", mount_point)
        return False

    return True
