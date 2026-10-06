from __future__ import annotations

from pathlib import Path
from subprocess import CalledProcessError
from typing import TYPE_CHECKING

import pytest

from batocera_common.fs import (
    LazyDetachFailedError,
    MountFailedError,
    UnmountFailedError,
    manage_mount,
    mount,
    unmount,
)

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from pytest_mock import MockerFixture

_MOUNT_POINT = Path('/mnt/test')
_DEVICE = Path('/dev/sda1')


def _create_process_error(cmd: str, stderr: str, /, *, returncode: int = 1) -> CalledProcessError:
    return CalledProcessError(returncode, [cmd], stderr=stderr)


@pytest.fixture
def mock_run(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch('batocera_common.fs.run', new_callable=mocker.AsyncMock)


@pytest.fixture
def mock_sleep(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch('asyncio.sleep', new_callable=mocker.AsyncMock)


class TestUnmount:
    async def test_succeeds_on_first_attempt(self, mock_run: AsyncMock) -> None:
        await unmount(_MOUNT_POINT)

        mock_run.assert_awaited_once_with('umount', _MOUNT_POINT, text=True, check=True)

    async def test_non_busy_failure_raises_unmount_failed_error(self, mock_run: AsyncMock) -> None:
        error = _create_process_error('umount', 'not mounted')
        mock_run.side_effect = error

        with pytest.raises(UnmountFailedError) as exc_info:
            await unmount(_MOUNT_POINT)

        assert exc_info.value.mount_point == _MOUNT_POINT
        assert exc_info.value.reason == 'not mounted'
        assert exc_info.value.__cause__ is error
        mock_run.assert_awaited_once_with('umount', _MOUNT_POINT, text=True, check=True)

    async def test_retries_while_busy_then_succeeds(self, mock_run: AsyncMock, mock_sleep: AsyncMock) -> None:
        mock_run.side_effect = [
            _create_process_error('umount', 'target is busy'),
            None,
        ]

        await unmount(_MOUNT_POINT, attempts=3, delay=0.1)

        assert mock_run.await_count == 2
        mock_sleep.assert_awaited_once_with(0.1)

    async def test_lazy_detaches_after_exhausted_busy_retries(self, mock_run: AsyncMock, mock_sleep: AsyncMock) -> None:
        busy = _create_process_error('umount', 'device is busy')
        mock_run.side_effect = [busy, busy, None]

        await unmount(_MOUNT_POINT, attempts=2, delay=0.01)

        assert mock_run.await_args_list == [
            (('umount', _MOUNT_POINT), {'text': True, 'check': True}),
            (('umount', _MOUNT_POINT), {'text': True, 'check': True}),
            (('umount', '-l', _MOUNT_POINT), {'text': True, 'check': True}),
        ]
        mock_sleep.assert_awaited_once_with(0.01)

    async def test_lazy_detach_failure_raises_lazy_detach_failed_error(
        self, mock_run: AsyncMock, mock_sleep: AsyncMock
    ) -> None:
        busy = _create_process_error('umount', 'target is busy')
        lazy_error = _create_process_error('umount', 'lazy failed')
        mock_run.side_effect = [busy, lazy_error]

        with pytest.raises(LazyDetachFailedError) as exc_info:
            await unmount(_MOUNT_POINT, attempts=1)

        assert exc_info.value.mount_point == _MOUNT_POINT
        assert exc_info.value.reason == 'lazy failed'
        assert exc_info.value.__cause__ is lazy_error
        mock_sleep.assert_not_awaited()


class TestMount:
    async def test_mounts_device_on_mount_point(self, mock_run: AsyncMock) -> None:
        await mount(_DEVICE, _MOUNT_POINT)

        mock_run.assert_awaited_once_with('mount', _DEVICE, _MOUNT_POINT, text=True, check=True)

    async def test_passes_type_and_options(self, mock_run: AsyncMock) -> None:
        await mount('overlay', _MOUNT_POINT, type='overlay', options='lowerdir=/a,upperdir=/b')

        mock_run.assert_awaited_once_with(
            'mount',
            '-t',
            'overlay',
            'overlay',
            '-o',
            'lowerdir=/a,upperdir=/b',
            _MOUNT_POINT,
            text=True,
            check=True,
        )

    async def test_failure_raises_mount_failed_error(self, mock_run: AsyncMock) -> None:
        error = RuntimeError('mount blew up')
        mock_run.side_effect = error

        with pytest.raises(MountFailedError) as exc_info:
            await mount(_DEVICE, _MOUNT_POINT)

        assert exc_info.value.mount_point == _MOUNT_POINT
        assert exc_info.value.__cause__ is error


class TestManageMount:
    async def test_yields_mount_point_and_unmounts_on_exit(self, mock_run: AsyncMock) -> None:
        async with manage_mount(_DEVICE, _MOUNT_POINT) as yielded:
            assert yielded is _MOUNT_POINT
            mock_run.assert_awaited_once_with('mount', _DEVICE, _MOUNT_POINT, text=True, check=True)

        assert mock_run.await_args_list == [
            (('mount', _DEVICE, _MOUNT_POINT), {'text': True, 'check': True}),
            (('umount', _MOUNT_POINT), {'text': True, 'check': True}),
        ]

    async def test_mount_failure_does_not_unmount(self, mock_run: AsyncMock) -> None:
        mock_run.side_effect = OSError('nope')

        with pytest.raises(MountFailedError):
            async with manage_mount(_DEVICE, _MOUNT_POINT):
                pass

        mock_run.assert_awaited_once_with('mount', _DEVICE, _MOUNT_POINT, text=True, check=True)

    async def test_unmount_failure_after_success_raises(self, mock_run: AsyncMock) -> None:
        unmount_error = _create_process_error('umount', 'still mounted')
        mock_run.side_effect = [None, unmount_error]

        with pytest.raises(UnmountFailedError) as exc_info:
            async with manage_mount(_DEVICE, _MOUNT_POINT):
                pass

        assert exc_info.value.mount_point == _MOUNT_POINT
        assert exc_info.value.reason == 'still mounted'

    async def test_body_error_propagates_when_unmount_succeeds(self, mock_run: AsyncMock) -> None:
        with pytest.raises(RuntimeError, match='body failed'):
            async with manage_mount(_DEVICE, _MOUNT_POINT):
                raise RuntimeError('body failed')

        assert mock_run.await_count == 2

    async def test_body_and_unmount_failure_raise_exception_group(self, mock_run: AsyncMock) -> None:
        mock_run.side_effect = [None, _create_process_error('umount', 'still mounted')]

        with pytest.raises(ExceptionGroup) as exc_info:
            async with manage_mount(_DEVICE, _MOUNT_POINT):
                raise ValueError('body failed')

        assert len(exc_info.value.exceptions) == 2
        assert isinstance(exc_info.value.exceptions[0], ValueError)
        assert str(exc_info.value.exceptions[0]) == 'body failed'
        assert isinstance(exc_info.value.exceptions[1], UnmountFailedError)

    async def test_soft_unmount_failure_preserves_body_error(self, mock_run: AsyncMock) -> None:
        mock_run.side_effect = [None, _create_process_error('umount', 'still mounted')]

        with pytest.raises(RuntimeError, match='body failed'):
            async with manage_mount(_DEVICE, _MOUNT_POINT, raise_on_unmount_failure=False):
                raise RuntimeError('body failed')

    async def test_soft_unmount_failure_alone_is_swallowed(self, mock_run: AsyncMock) -> None:
        mock_run.side_effect = [None, _create_process_error('umount', 'still mounted')]

        async with manage_mount(_DEVICE, _MOUNT_POINT, raise_on_unmount_failure=False):
            pass

    async def test_forwards_unmount_retry_settings(self, mocker: MockerFixture, mock_run: AsyncMock) -> None:
        mock_unmount = mocker.patch('batocera_common.fs.unmount', new_callable=mocker.AsyncMock)

        async with manage_mount(_DEVICE, _MOUNT_POINT, unmount_attempts=3, unmount_delay=0.25):
            pass

        mock_unmount.assert_awaited_once_with(_MOUNT_POINT, attempts=3, delay=0.25)
