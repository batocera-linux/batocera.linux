from __future__ import annotations

import asyncio
import locale
import logging
import sys
from contextlib import AbstractAsyncContextManager, AsyncExitStack, asynccontextmanager
from dataclasses import dataclass
from subprocess import CalledProcessError
from typing import TYPE_CHECKING, Any, Final, Literal, overload

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from pathlib import Path

_logger: Final = logging.getLogger(__name__)


@dataclass(slots=True)
class AsyncCompletedProcess[T]:
    returncode: int
    stdout: T
    stderr: T


def _text_encoding() -> str:
    if sys.flags.utf8_mode:
        return 'utf-8'

    return locale.getencoding()


def _decode(data: bytes, encoding: str, /) -> str:
    text = data.decode(encoding)
    return text.replace('\r\n', '\n').replace('\r', '\n')


@overload
async def run(
    cmd: str | Path,
    /,
    *args: str | Path,
    check: bool = ...,
    shell: Literal[False] = False,
    text: Literal[False] = False,
) -> AsyncCompletedProcess[bytes]: ...


@overload
async def run(
    cmd: str | Path, /, *args: str | Path, check: bool = ..., shell: Literal[False] = False, text: Literal[True]
) -> AsyncCompletedProcess[str]: ...


@overload
async def run(
    cmd: str, /, *args: str, check: bool = ..., text: Literal[False] = False, shell: Literal[True]
) -> AsyncCompletedProcess[bytes]: ...


@overload
async def run(
    cmd: str, /, *args: str, check: bool = ..., shell: Literal[True], text: Literal[True]
) -> AsyncCompletedProcess[str]: ...


async def run(
    cmd: Any, /, *args: Any, shell: bool = False, check: bool = False, text: bool = False
) -> AsyncCompletedProcess[Any]:
    if shell:
        proc = await asyncio.create_subprocess_shell(
            ' '.join([cmd, *args]), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
    else:
        proc = await asyncio.create_subprocess_exec(
            cmd, *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
    (out, err) = await proc.communicate()
    return_code = await proc.wait()

    if text:
        encoding = _text_encoding()
        out = _decode(out, encoding)
        err = _decode(err, encoding)

    if check and return_code:
        raise CalledProcessError(return_code, cmd)

    return AsyncCompletedProcess(returncode=return_code, stdout=out, stderr=err)


@overload
async def group_tasks[T1](
    coro1: asyncio._CoroutineLike[T1],
    /,
) -> tuple[T1]: ...
@overload
async def group_tasks[T1, T2](
    coro1: asyncio._CoroutineLike[T1],
    coro2: asyncio._CoroutineLike[T2],
    /,
) -> tuple[T1, T2]: ...
@overload
async def group_tasks[T1, T2, T3](
    coro1: asyncio._CoroutineLike[T1],
    coro2: asyncio._CoroutineLike[T2],
    coro3: asyncio._CoroutineLike[T3],
    /,
) -> tuple[T1, T2, T3]: ...
@overload
async def group_tasks[T1, T2, T3, T4](
    coro1: asyncio._CoroutineLike[T1],
    coro2: asyncio._CoroutineLike[T2],
    coro3: asyncio._CoroutineLike[T3],
    coro4: asyncio._CoroutineLike[T4],
    /,
) -> tuple[T1, T2, T3, T4]: ...


async def group_tasks(*coros: asyncio._CoroutineLike[Any]) -> tuple[Any, ...]:
    """Run multiple coroutines concurrently and return their results as a tuple.

    Unlike `asyncio.gather`, this function will raise the first exception that occurs
    in any of the coroutines, and will cancel all other coroutines.
    """

    async with asyncio.TaskGroup() as task_group:
        tasks = [task_group.create_task(coro) for coro in coros]

    return tuple(task.result() for task in tasks)


@overload
def parallel[T1](
    manager1: AbstractAsyncContextManager[T1],
    /,
) -> AbstractAsyncContextManager[tuple[T1]]: ...
@overload
def parallel[T1, T2](
    manager1: AbstractAsyncContextManager[T1],
    manager2: AbstractAsyncContextManager[T2],
    /,
) -> AbstractAsyncContextManager[tuple[T1, T2]]: ...
@overload
def parallel[T1, T2, T3](
    manager1: AbstractAsyncContextManager[T1],
    manager2: AbstractAsyncContextManager[T2],
    manager3: AbstractAsyncContextManager[T3],
    /,
) -> AbstractAsyncContextManager[tuple[T1, T2, T3]]: ...
@overload
def parallel[T1, T2, T3, T4](
    manager1: AbstractAsyncContextManager[T1],
    manager2: AbstractAsyncContextManager[T2],
    manager3: AbstractAsyncContextManager[T3],
    manager4: AbstractAsyncContextManager[T4],
    /,
) -> AbstractAsyncContextManager[tuple[T1, T2, T3, T4]]: ...


@asynccontextmanager
async def parallel(*managers: AbstractAsyncContextManager[Any]) -> AsyncGenerator[tuple[Any, ...]]:
    """Enter multiple async context managers concurrently and yield their results as a tuple.

    If any of the context managers fails to enter, the others will be exited in reverse order
    of the order they were passed to the function.
    """

    results: list[Any] = [None] * len(managers)
    entered = [False] * len(managers)

    async with AsyncExitStack() as stack:

        async def _enter(index: int, manager: AbstractAsyncContextManager[Any]) -> None:
            results[index] = await manager.__aenter__()
            entered[index] = True

        try:
            async with asyncio.TaskGroup() as task_group:
                for index, manager in enumerate(managers):
                    task_group.create_task(_enter(index, manager))
        finally:
            for index, manager in enumerate(managers):
                if entered[index]:
                    # Register the exit of the entered context manager with the stack, so that it
                    # will be called in reverse order of entry, even if an exception occurs in one
                    # of the context managers.
                    stack.push_async_exit(manager)

        # If any of the context managers fails to enters, the following line
        # never executes
        yield tuple(results)


async def is_connected_to_internet() -> bool:
    # Try Cloudflare one.one.one.one first
    try:
        await run('timeout', '1', 'ping', '-c', '1', '-t', '255', 'one.one.one.one', check=True)
    except CalledProcessError:
        try:
            # Try dns.google if one.one.one.one fails
            await run('timeout', '1', 'ping', '-c', '1', '-t', '255', 'dns.google', check=True)
        except CalledProcessError:
            _logger.error('Not connected to the internet')
            return False

    _logger.debug('Connected to the internet')
    return True
