from __future__ import annotations

import logging
import os
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Final, overload
from typing_extensions import Sentinel

from batocera_common.asyncio import run

from .paths import SYSTEM_SCRIPTS, USER_SCRIPTS

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Iterable, Mapping

    import aiohttp

_logger: Final = logging.getLogger(__name__)


async def call_script(directory: Path, event: str, args: Iterable[str | Path], /) -> None:
    if not directory.is_dir():
        return

    for file in directory.iterdir():
        if file.is_dir():
            await call_script(file, event, args)
        elif os.access(file, os.X_OK):
            _logger.debug('calling script: %s', [file, event, *args])
            await run(file, event, *args)


@asynccontextmanager
async def script_caller(events: tuple[Iterable[str], Iterable[str]], /, *args: str | Path) -> AsyncGenerator[None]:
    before_events, after_events = events

    if isinstance(before_events, str):
        before_events = [before_events]

    if isinstance(after_events, str):
        after_events = [after_events]

    for event in before_events:
        for directory in (SYSTEM_SCRIPTS, USER_SCRIPTS):
            await call_script(directory, event, args)

    try:
        yield
    finally:
        for event in after_events:
            for directory in (USER_SCRIPTS, SYSTEM_SCRIPTS):
                await call_script(directory, event, args)


_MISSING = Sentinel('_MISSING')


@overload
def download(
    session: aiohttp.ClientSession,
    url: str,
    target_dir: Path,
    /,
    *,
    headers: Mapping[str, str] | None = None,
    timeout: aiohttp.ClientTimeout | None = None,
    etag: _MISSING = _MISSING,
) -> AbstractAsyncContextManager[Path]: ...


@overload
def download(
    session: aiohttp.ClientSession,
    url: str,
    target_dir: Path,
    /,
    *,
    headers: Mapping[str, str] | None = None,
    timeout: aiohttp.ClientTimeout | None = None,
    etag: str | None,
) -> AbstractAsyncContextManager[tuple[Path | None, str | None]]: ...


@asynccontextmanager
async def download(
    session: aiohttp.ClientSession,
    url: str,
    target_dir: Path,
    /,
    *,
    headers: Mapping[str, str] | None = None,
    timeout: aiohttp.ClientTimeout | None = None,
    etag: str | _MISSING | None = _MISSING,
) -> AsyncGenerator[tuple[Path | None, str | None] | Path]:
    headers = {} if headers is None else dict(headers)

    if etag and etag is not _MISSING:
        headers['If-None-Match'] = etag

    target_dir.mkdir(parents=True, exist_ok=True)

    _logger.debug('Downloading %s...', url)

    async with session.get(url, headers=headers, timeout=timeout) as response:
        if etag and etag is not _MISSING and response.status == 304:  # 304: Not Modified
            _logger.debug('%s is not modified', url)
            yield None, None
            return

        response.raise_for_status()

        with NamedTemporaryFile(dir=target_dir, delete_on_close=False) as file:
            async for chunk in response.content.iter_chunked(64 * 1024):
                file.write(chunk)

            file.close()  # Close the file to ensure all data is flushed to disk

            temp_path = Path(file.name)

            if etag is not _MISSING:
                yield temp_path, response.headers.getone('ETag', '').strip() or None
            else:
                yield temp_path
