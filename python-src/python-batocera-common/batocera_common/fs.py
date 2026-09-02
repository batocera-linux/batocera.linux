from __future__ import annotations

import asyncio
import filecmp
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from subprocess import CalledProcessError
from typing import TYPE_CHECKING

from .asyncio import run

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Iterator


_logger = logging.getLogger(__name__)


type Difference = tuple[None, Path] | tuple[Path, None] | tuple[Path, Path]


def _dircmp_differences(comparison: filecmp.dircmp[str], /) -> Iterator[Difference]:
    left = Path(comparison.left)
    right = Path(comparison.right)

    yield from ((left / name, None) for name in comparison.left_only)
    yield from ((None, right / name) for name in comparison.right_only)
    yield from (
        (left / name, right / name) for name in comparison.diff_files + comparison.funny_files + comparison.common_funny
    )

    for sub in comparison.subdirs.values():
        yield from _dircmp_differences(sub)


@dataclass(slots=True)
class directory_differences:
    left: Path
    right: Path

    _differences: tuple[Difference, ...] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        comparison = filecmp.dircmp(self.left, self.right, shallow=False)
        self._differences = tuple(_dircmp_differences(comparison))

    def __bool__(self) -> bool:
        return bool(self._differences)

    def report(self) -> str:
        if not self._differences:
            return 'Directories are identical'

        left_only: list[Path] = []
        right_only: list[Path] = []
        different: list[Path] = []

        for difference in self._differences:
            if difference[0] is not None:
                if difference[1] is None:
                    left_only.append(difference[0])
                else:
                    different.append(difference[0])
            else:
                right_only.append(difference[1])

        report: list[str] = []

        if left_only:
            report.append(f'Missing in {self.right}:')
            report.extend(f'  {path.relative_to(self.left)}' for path in left_only)

        if right_only:
            report.append(f'Extra in {self.right}:')
            report.extend(f'  {path.relative_to(self.right)}' for path in right_only)

        if different:
            report.append('Different files:')
            report.extend(f'  {path.relative_to(self.left)}' for path in different)

        return '\n'.join(report)


class MountingError(OSError):
    mount_point: Path

    def __init__(self, mount_point: Path, /, *args: object) -> None:
        self.mount_point = mount_point

        super().__init__(*args, mount_point)


class MountFailedError(MountingError): ...


class UnmountFailedError(MountingError):
    reason: str

    def __init__(self, mount_point: Path, reason: str, /) -> None:
        self.reason = reason

        super().__init__(mount_point, reason)


class LazyDetachFailedError(UnmountFailedError): ...


async def unmount(mount_point: Path, /, *, attempts: int = 10, delay: float = 0.5) -> None:
    """Unmount ``mount_point``, retrying while the mount is busy.

    A game that was killed rather than closed can leave processes holding the
    mount while they die, so a busy mount is worth waiting on rather than giving
    up immediately. After ``attempts`` failures that report busy, falls back to
    a lazy detach (``umount -l``) so the path is released even if open file
    descriptors remain — otherwise the underlying device (for example a ROM
    squashfs) can stay busy until reboot.

    Args:
        mount_point: Path currently used as a mount point.
        attempts: How many normal ``umount`` tries before lazy-detaching.
        delay: Seconds to sleep between busy retries.

    Raises:
        UnmountFailedError: ``umount`` failed for a reason other than busy.
        LazyDetachFailedError: Lazy ``umount -l`` also failed.
    """
    for attempt in range(attempts):
        try:
            await run('umount', mount_point, text=True, check=True)
            return
        except CalledProcessError as e:
            if e.returncode != 0 and 'busy' not in (stderr := (e.stderr or '').strip()):
                # No need to retry if the device isn't busy. Log it and raise.
                _logger.exception("Failed to unmount '%s' because %s", mount_point, stderr)

                raise UnmountFailedError(mount_point, stderr) from e

        if not attempt:
            # Log on the first attempt only, to avoid spamming the logs
            _logger.debug("'%s' is busy, waiting for it to be released", mount_point)

        if attempt < attempts - 1:
            await asyncio.sleep(delay)

    _logger.warning("'%s' is still busy, detaching it lazily", mount_point)

    try:
        # detach it anyway, the kernel drops it once the last process lets go: leaving it
        # mounted would keep the rom busy until the next reboot
        await run('umount', '-l', mount_point, text=True, check=True)
    except CalledProcessError as e:
        stderr = (e.stderr or '').strip()
        _logger.exception("Failed to lazily detach '%s' because %s", mount_point, stderr)

        raise LazyDetachFailedError(mount_point, stderr) from e


async def mount(
    device: Path | str,
    mount_point: Path,
    /,
    *,
    type: str | None = None,
    options: str | None = None,
) -> None:
    """Mount ``device`` on ``mount_point``.

    Args:
        device: Source to mount (path, or a pseudo-device name such as
            ``'overlay'``).
        mount_point: Directory that becomes the mount point.
        type: Filesystem type passed as ``mount -t`` when set.
        options: Mount options passed as ``mount -o`` when set.

    Raises:
        MountFailedError: The ``mount`` command failed. The original error is
            available as ``__cause__``.
    """
    try:
        type_args = ('-t', type) if type is not None else ()
        option_args = ('-o', options) if options is not None else ()

        await run('mount', *type_args, device, *option_args, mount_point, text=True, check=True)
    except Exception as e:
        raise MountFailedError(mount_point) from e


@asynccontextmanager
async def manage_mount(
    device: Path | str,
    mount_point: Path,
    /,
    *,
    type: str | None = None,
    options: str | None = None,
    unmount_attempts: int = 10,
    unmount_delay: float = 0.5,
    raise_on_unmount_failure: bool = True,
) -> AsyncGenerator[Path]:
    """Mount ``device`` for the duration of the context, then unmount it.

    Yields ``mount_point`` after a successful :func:`mount`. On exit, always
    attempts :func:`unmount` (including when the body raised).

    When unmount fails and ``raise_on_unmount_failure`` is true:

    - If the body also raised, both errors are raised together as an
      :class:`ExceptionGroup` (body error first) so neither is lost.
    - Otherwise the :class:`UnmountFailedError` is re-raised alone.

    When ``raise_on_unmount_failure`` is false, unmount failures are swallowed
    after :func:`unmount` has logged them, so a body exception (if any) still
    propagates. Use that for soft-fail teardown (for example overlayfs).

    Args:
        device: Source passed to :func:`mount`.
        mount_point: Mount point path; also the value yielded by the context.
        type: Optional filesystem type for :func:`mount`.
        options: Optional mount options for :func:`mount`.
        unmount_attempts: Forwarded to :func:`unmount` as ``attempts``.
        unmount_delay: Forwarded to :func:`unmount` as ``delay``.
        raise_on_unmount_failure: If false, log and ignore unmount failures.

    Yields:
        The ``mount_point`` path after the filesystem is mounted.

    Raises:
        MountFailedError: Initial mount failed.
        UnmountFailedError: Unmount failed and ``raise_on_unmount_failure`` is
            true with no body exception.
        ExceptionGroup: Body and unmount both failed and
            ``raise_on_unmount_failure`` is true.
    """
    await mount(device, mount_point, type=type, options=options)

    body_error: Exception | None = None

    try:
        yield mount_point
    except Exception as e:
        body_error = e
        raise
    finally:
        try:
            await unmount(mount_point, attempts=unmount_attempts, delay=unmount_delay)
        except UnmountFailedError as unmount_error:
            if raise_on_unmount_failure:
                if body_error is not None:
                    # In order to avoid losing either of the original exception or the unmount exception,
                    # we raise an ExceptionGroup that contains both the body error and the unmount error.
                    # This allows both exceptions to end up in the Python logging output.
                    raise ExceptionGroup(
                        'Failed to unmount after an error in the body', [body_error, unmount_error]
                    ) from None
                else:
                    raise
