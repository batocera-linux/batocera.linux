from __future__ import annotations

import asyncio
import locale
import logging
import os
import sys
import threading
from contextlib import AbstractAsyncContextManager, AsyncExitStack, asynccontextmanager
from dataclasses import dataclass
from subprocess import CalledProcessError
from typing import TYPE_CHECKING, Any, Concatenate, Final, Literal, cast, overload

import aiohttp

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Awaitable, Callable, Coroutine
    from pathlib import Path
    from subprocess import _ENV

_logger: Final = logging.getLogger(__name__)


def run_in_new_uvloop[T](coro: Awaitable[T], /) -> T:
    """Run a coroutine in a fresh thread with its own uvloop."""
    import uvloop

    result: list[T] = []

    def runner() -> None:
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result.append(loop.run_until_complete(coro))
        finally:
            loop.close()

    t = threading.Thread(target=runner)
    t.start()
    t.join()
    return result[0]


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


def env_to_fspath(env: _ENV | None, /) -> dict[str, str | bytes] | dict[bytes, str | bytes] | None:
    if env is None:
        return None

    return {cast('Any', key): os.fspath(value) for key, value in env.items()}


@overload
async def run(
    cmd: str | Path,
    /,
    *args: str | Path,
    check: bool = ...,
    shell: bool = ...,
    text: bool = ...,
    capture_output: Literal[False],
    env: _ENV | None = None,
) -> AsyncCompletedProcess[None]: ...


@overload
async def run(
    cmd: str | Path,
    /,
    *args: str | Path,
    check: bool = ...,
    shell: Literal[False] = False,
    text: Literal[False] = False,
    capture_output: Literal[True] = True,
    env: _ENV | None = None,
) -> AsyncCompletedProcess[bytes]: ...


@overload
async def run(
    cmd: str | Path,
    /,
    *args: str | Path,
    check: bool = ...,
    shell: Literal[False] = False,
    text: Literal[True],
    capture_output: Literal[True] = True,
    env: _ENV | None = None,
) -> AsyncCompletedProcess[str]: ...


@overload
async def run(
    cmd: str,
    /,
    *args: str,
    check: bool = ...,
    text: Literal[False] = False,
    shell: Literal[True],
    capture_output: Literal[True] = True,
    env: _ENV | None = None,
) -> AsyncCompletedProcess[bytes]: ...


@overload
async def run(
    cmd: str,
    /,
    *args: str,
    check: bool = ...,
    shell: Literal[True],
    text: Literal[True],
    capture_output: Literal[True] = True,
    env: _ENV | None = None,
) -> AsyncCompletedProcess[str]: ...


async def run(
    cmd: Any,
    /,
    *args: Any,
    shell: bool = False,
    check: bool = False,
    text: bool = False,
    capture_output: bool = True,
    env: _ENV | None = None,
) -> AsyncCompletedProcess[Any]:
    io = asyncio.subprocess.PIPE if capture_output else asyncio.subprocess.DEVNULL

    if shell:
        proc = await asyncio.create_subprocess_shell(
            ' '.join([cmd, *args]),
            stdout=io,
            stderr=io,
            env=env_to_fspath(env),
        )
    else:
        proc = await asyncio.create_subprocess_exec(
            cmd,
            *args,
            stdout=io,
            stderr=io,
            env=env_to_fspath(env),
        )

    if capture_output:
        (out, err) = await proc.communicate()
    else:
        out = err = None

    return_code = await proc.wait()

    if text and out is not None and err is not None:
        encoding = _text_encoding()
        out = _decode(out, encoding)
        err = _decode(err, encoding)

    if check and return_code:
        raise CalledProcessError(return_code, cmd, output=out, stderr=err)

    return AsyncCompletedProcess(returncode=return_code, stdout=out, stderr=err)


@overload
async def group_tasks() -> tuple[()]: ...
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
def parallel() -> AbstractAsyncContextManager[tuple[()]]: ...
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


async def create_ready_task[**P, R](
    callable: Callable[Concatenate[asyncio.Event, P], Coroutine[Any, Any, R]],
    /,
    *args: P.args,
    **kwargs: P.kwargs,
) -> asyncio.Task[R]:
    """Start a coroutine as a background task and wait until it signals readiness.

    The callable receives an `asyncio.Event` as its first argument (followed by
    any additional `*args` / `**kwargs`). It must call `ready.set()` once its
    initialization is complete. This function returns only after that signal,
    with the task still running in the background.
    """

    ready = asyncio.Event()
    task = asyncio.create_task(callable(ready, *args, **kwargs))

    await ready.wait()

    return task


async def is_connected_to_internet() -> bool:
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1)) as session:
        try:
            async with session.head('https://one.one.one.one'):
                return True
        except aiohttp.ClientError, TimeoutError:
            try:
                async with session.head('https://dns.google'):
                    return True
            except aiohttp.ClientError, TimeoutError:
                _logger.error('Not connected to the internet')
                return False
