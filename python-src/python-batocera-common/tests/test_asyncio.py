from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

import pytest

from batocera_common.asyncio import create_ready_task, group_tasks, parallel

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


class TestParallel:
    async def test_single_manager_result(self) -> None:
        @asynccontextmanager
        async def manager() -> AsyncGenerator[str]:
            yield 'ok'

        async with parallel(manager()) as results:
            assert results == ('ok',)

    async def test_yields_results_in_order(self) -> None:
        @asynccontextmanager
        async def manager(value: int) -> AsyncGenerator[int]:
            yield value

        async with parallel(manager(1), manager(2), manager(3)) as results:
            assert results == (1, 2, 3)

    async def test_empty_parallel_yields_empty_tuple(self) -> None:
        async with parallel() as results:
            assert results == ()

    async def test_enters_concurrently(self) -> None:
        barrier = asyncio.Barrier(2)
        started = 0

        @asynccontextmanager
        async def manager(value: str) -> AsyncGenerator[str]:
            nonlocal started
            started += 1
            await barrier.wait()
            yield value

        async with parallel(manager('a'), manager('b')) as results:
            assert results == ('a', 'b')
            assert started == 2

    async def test_exits_in_reverse_order(self) -> None:
        log: list[str] = []

        @asynccontextmanager
        async def manager(name: str) -> AsyncGenerator[str]:
            try:
                yield name
            finally:
                log.append(f'exit:{name}')

        async with parallel(manager('a'), manager('b'), manager('c')) as results:
            assert results == ('a', 'b', 'c')
            assert log == []

        assert log == ['exit:c', 'exit:b', 'exit:a']

    async def test_exits_on_body_exception(self) -> None:
        log: list[str] = []

        @asynccontextmanager
        async def manager(name: str) -> AsyncGenerator[str]:
            try:
                yield name
            finally:
                log.append(f'exit:{name}')

        with pytest.raises(RuntimeError, match='body'):
            async with parallel(manager('a'), manager('b')):
                raise RuntimeError('body')

        assert log == ['exit:b', 'exit:a']

    async def test_enter_failure_exits_entered_managers(self) -> None:
        log: list[str] = []
        ok_entered = asyncio.Event()

        @asynccontextmanager
        async def ok() -> AsyncGenerator[str]:
            log.append('enter:ok')
            ok_entered.set()
            try:
                yield 'ok'
            finally:
                log.append('exit:ok')

        class Fail:
            async def __aenter__(self) -> None:
                await ok_entered.wait()
                raise ValueError('boom')

            async def __aexit__(self, *args: object) -> None:
                return None

        with pytest.raises(ExceptionGroup) as exc_info:
            async with parallel(ok(), Fail()):
                pass

        assert log == ['enter:ok', 'exit:ok']
        assert any(isinstance(exc, ValueError) and str(exc) == 'boom' for exc in exc_info.value.exceptions)


class TestGroupTasks:
    async def test_single_coroutine_result(self) -> None:
        async def worker() -> str:
            return 'ok'

        assert await group_tasks(worker()) == ('ok',)

    async def test_returns_results_in_order(self) -> None:
        async def worker(value: int) -> int:
            await asyncio.sleep(0)
            return value

        assert await group_tasks(worker(1), worker(2), worker(3)) == (1, 2, 3)

    async def test_empty_group_returns_empty_tuple(self) -> None:
        assert await group_tasks() == ()

    async def test_runs_concurrently(self) -> None:
        barrier = asyncio.Barrier(2)
        started = 0

        async def worker(value: int) -> int:
            nonlocal started
            started += 1
            await barrier.wait()
            return value

        assert await group_tasks(worker(1), worker(2)) == (1, 2)
        assert started == 2

    async def test_failure_cancels_siblings_and_raises(self) -> None:
        cancelled = asyncio.Event()

        async def fail() -> None:
            raise ValueError('boom')

        async def hang() -> None:
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                cancelled.set()
                raise

        with pytest.raises(ExceptionGroup) as exc_info:
            await group_tasks(fail(), hang())

        assert cancelled.is_set()
        assert any(isinstance(exc, ValueError) and str(exc) == 'boom' for exc in exc_info.value.exceptions)


class TestCreateReadyTask:
    async def test_returns_running_task_after_ready(self) -> None:
        started = asyncio.Event()

        async def worker(ready: asyncio.Event) -> str:
            started.set()
            ready.set()
            await asyncio.Event().wait()
            return 'unreachable'

        task = await create_ready_task(worker)

        assert isinstance(task, asyncio.Task)
        assert started.is_set()
        assert not task.done()

        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    async def test_waits_until_ready_is_set(self) -> None:
        proceed = asyncio.Event()
        returned = False

        async def worker(ready: asyncio.Event) -> None:
            await proceed.wait()
            ready.set()

        async def create() -> asyncio.Task[None]:
            nonlocal returned
            task = await create_ready_task(worker)
            returned = True
            return task

        create_task = asyncio.create_task(create())
        await asyncio.sleep(0)

        assert not returned
        assert not create_task.done()

        proceed.set()
        task = await create_task

        assert returned
        await task

    async def test_passes_args_and_kwargs(self) -> None:
        async def worker(ready: asyncio.Event, value: int, *, label: str) -> tuple[int, str]:
            ready.set()
            return value, label

        task = await create_ready_task(worker, 7, label='ok')

        assert await task == (7, 'ok')

    async def test_task_result_available_after_completion(self) -> None:
        async def worker(ready: asyncio.Event) -> int:
            ready.set()
            await asyncio.sleep(0)
            return 42

        task = await create_ready_task(worker)

        assert await task == 42

    async def test_exception_after_ready_propagates_via_task(self) -> None:
        async def worker(ready: asyncio.Event) -> None:
            ready.set()
            raise RuntimeError('boom')

        task = await create_ready_task(worker)

        with pytest.raises(RuntimeError, match='boom'):
            await task
