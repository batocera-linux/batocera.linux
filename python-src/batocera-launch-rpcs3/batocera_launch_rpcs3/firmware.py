from __future__ import annotations

import asyncio
import hashlib
import logging
import re
import shutil
import struct
import time
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING, Final, NamedTuple, Self

import aiohttp

from batocera_common.asyncio import run
from batocera_common.paths import BIOS, CACHE
from batocera_launch.exceptions import BaseBatoceraException

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Mapping
    from pathlib import Path
    from types import TracebackType

_logger: Final = logging.getLogger(__name__)

PUP_PATH: Final = BIOS / 'PS3UPDAT.PUP'
_PART_PATH: Final = BIOS / '.PS3UPDAT.PUP.part'
_UPDATE_LIST_URL: Final = 'http://fus01.ps3.update.playstation.net/update/ps3/list/us/ps3-updatelist.txt'
_STATE_DIR: Final = CACHE / 'rpcs3' / 'firmware-update'
_CHECKED_PATH: Final = _STATE_DIR / 'checked'
_PENDING_PATH: Final = _STATE_DIR / 'pending'
_CHECK_INTERVAL: Final = 24 * 60 * 60
_MAX_PUP_ENTRIES: Final = 64


class Release(NamedTuple):
    version: Decimal
    url: str


def _to_decimal(version: str) -> Decimal | None:
    try:
        return Decimal(version.strip())
    except InvalidOperation:
        return None


def format_version(version: Decimal | None, /) -> str:
    return 'unknown' if version is None else f'{version:.2f}'


def installed_version(config_dir: Path, /) -> Decimal | None:
    try:
        text = (config_dir / 'dev_flash' / 'vsh' / 'etc' / 'version.txt').read_text(errors='replace')
    except OSError:
        return None

    if matches := re.search(r'^release:(.*?):', text, re.MULTILINE):
        return _to_decimal(matches[1])
    return None


def pup_version(path: Path = PUP_PATH, /) -> Decimal | None:
    # PUP header: magic, package/image version, file count, header/data length (all u64 BE),
    # then 32-byte entries of (id, offset, length, pad); entry 0x100 holds the version string.
    try:
        with path.open('rb') as stream:
            header = stream.read(48)
            if len(header) < 48 or header[:5] != b'SCEUF':
                return None

            file_count = min(struct.unpack_from('>Q', header, 24)[0], _MAX_PUP_ENTRIES)
            entries = stream.read(file_count * 32)
            for index in range(len(entries) // 32):
                entry_id, offset, length, _ = struct.unpack_from('>QQQQ', entries, index * 32)
                if entry_id == 0x100:
                    stream.seek(offset)
                    return _to_decimal(stream.read(min(length, 32)).decode('ascii', 'replace').split('\n')[0])
    except OSError:
        return None
    return None


def parse_update_list(text: str, /) -> Release | None:
    for line in text.splitlines():
        fields = dict(field.split('=', 1) for field in line.split(';') if '=' in field)
        if fields.get('CDN', '').endswith('/PS3UPDAT.PUP') and (
            version := _to_decimal(fields.get('SystemSoftwareVersion', ''))
        ):
            return Release(version, fields['CDN'])
    return None


async def install(binary: Path, env: Mapping[str, str | Path], config_dir: Path, /) -> Decimal | None:
    # --headless installs without the confirmation dialogs; it aborts during teardown after a
    # successful install, so the result is read back from version.txt rather than the exit code.
    _logger.info('Installing PS3 firmware %s', format_version(pup_version()))
    await run(binary, '--headless', '--installfw', PUP_PATH, capture_output=False, env=env)
    return installed_version(config_dir)


def _current_version(config_dir: Path, /) -> Decimal | None:
    return max(filter(None, (installed_version(config_dir), pup_version())), default=None)


def _pending() -> Release | None:
    try:
        version, url = _PENDING_PATH.read_text().split(maxsplit=1)
    except OSError, ValueError:
        return None
    if pending := _to_decimal(version):
        return Release(pending, url.strip())
    return None


async def check(session: aiohttp.ClientSession, config_dir: Path, /, *, force: bool = False) -> Release | None:
    # An interrupted download is resumed while it is still newer; Sony's list is read at most once a day.
    current = _current_version(config_dir)

    if pending := _pending():
        if current is None or pending.version > current:
            return pending
        _PENDING_PATH.unlink(missing_ok=True)
        _PART_PATH.unlink(missing_ok=True)

    if not force and _CHECKED_PATH.exists() and time.time() - _CHECKED_PATH.stat().st_mtime < _CHECK_INTERVAL:
        return None

    async with session.get(_UPDATE_LIST_URL, timeout=aiohttp.ClientTimeout(total=15)) as response:
        response.raise_for_status()
        release = parse_update_list(await response.text(errors='replace'))

    _STATE_DIR.mkdir(parents=True, exist_ok=True)
    _CHECKED_PATH.touch()

    if release is None:
        _logger.warning('No PS3UPDAT.PUP entry in %s', _UPDATE_LIST_URL)
        return None

    if current is not None and current >= release.version:
        return None

    _PENDING_PATH.write_text(f'{release.version} {release.url}\n')
    return release


def _md5(path: Path, /) -> str:
    digest = hashlib.md5()
    with path.open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


async def download(
    session: aiohttp.ClientSession, release: Release, /, progress: Callable[[int], Awaitable[None]] | None = None
) -> None:
    BIOS.mkdir(parents=True, exist_ok=True)
    offset = _PART_PATH.stat().st_size if _PART_PATH.exists() else 0
    headers = {'Range': f'bytes={offset}-'} if offset else {}
    _logger.info(
        'Downloading PS3 firmware %s from %s (from byte %d)', format_version(release.version), release.url, offset
    )

    async with session.get(release.url, headers=headers, timeout=aiohttp.ClientTimeout(sock_read=60)) as response:
        if response.status != 416:  # 416: the part file is already complete
            if 400 <= response.status < 500:
                _PART_PATH.unlink(missing_ok=True)
                _PENDING_PATH.unlink(missing_ok=True)
            response.raise_for_status()
            done = offset if response.status == 206 else 0
            total = done + (response.content_length or 0)
            with _PART_PATH.open('ab' if response.status == 206 else 'wb') as out:
                async for chunk in response.content.iter_chunked(1024 * 1024):
                    out.write(chunk)
                    done += len(chunk)
                    if progress is not None and total:
                        await progress(min(done * 100 // total, 100))

    # Sony's CDN path carries the image md5.
    expected = re.search(r'_([0-9a-f]{32})/', release.url)
    version = pup_version(_PART_PATH)
    if (expected and expected[1] != await asyncio.to_thread(_md5, _PART_PATH)) or version != release.version:
        _PART_PATH.unlink(missing_ok=True)
        _PENDING_PATH.unlink(missing_ok=True)
        raise ValueError(f'{release.url} failed verification (PUP version {format_version(version)})')

    _PART_PATH.chmod(0o644)
    _PART_PATH.replace(PUP_PATH)
    _PENDING_PATH.unlink(missing_ok=True)
    _logger.info('PS3 firmware %s saved to %s', format_version(release.version), PUP_PATH)


async def update(session: aiohttp.ClientSession, config_dir: Path, /) -> None:
    # The new PUP is installed by the next launch, not under the running game.
    if release := await check(session, config_dir):
        await download(session, release)


def _markup(text: str, /) -> str:
    return f'--text=<span size="x-large">{text}</span>'


class Dialog:
    # yad is only built for Xorg/GTK boards; elsewhere everything runs without a dialog.

    def __init__(self) -> None:
        self._proc: asyncio.subprocess.Process | None = None
        self._last = -1

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> None:
        await self.close()

    async def status(self, text: str, /) -> None:
        # the progress bar label is small and faint, so each status gets its own window text
        await self.close()
        if not shutil.which('yad'):
            return
        self._proc = await asyncio.create_subprocess_exec(
            'yad',
            '--progress',
            '--title=PS3 Firmware',
            _markup(text),
            '--no-buttons',
            '--center',
            '--width=700',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        self._last = -1

    async def progress(self, percent: int, /) -> None:
        if self._proc is None or self._proc.stdin is None or percent == self._last:
            return
        self._last = percent
        try:
            self._proc.stdin.write(f'{percent}\n'.encode())
            await self._proc.stdin.drain()
        except BrokenPipeError, ConnectionResetError:
            pass

    async def close(self) -> None:
        if self._proc is not None:
            if self._proc.returncode is None:
                self._proc.terminate()
            await self._proc.wait()
            self._proc = None


class FirmwareMissing(BaseBatoceraException):
    # not a BatoceraException, so ES shows no error popup on top of the yad message
    pass


async def show_error(text: str, /) -> bool:
    if not shutil.which('yad'):
        return False
    await run(
        'yad',
        '--title=PS3 Firmware',
        '--image=dialog-error',
        _markup(text),
        '--no-buttons',
        '--timeout=3',
        '--center',
        '--width=700',
        capture_output=False,
    )
    return True
