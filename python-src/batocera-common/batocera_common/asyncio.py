from __future__ import annotations

import asyncio
import locale
import logging
import sys
from dataclasses import dataclass
from subprocess import CalledProcessError
from typing import TYPE_CHECKING, Any, Final, Literal, overload

if TYPE_CHECKING:
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
