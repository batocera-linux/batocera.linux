from __future__ import annotations

import hashlib
import struct
from decimal import Decimal
from typing import TYPE_CHECKING

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import BaseTestServer, TestServer
from batocera_launch_rpcs3 import firmware

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from pathlib import Path

_UPDATE_LIST = """# US
Dest=84;CompatibleSystemSoftwareVersion=4.9300-;
Dest=84;IncrementalUpdateVersion=00010b72-00010b72;ImageVersion=00010b94;SystemSoftwareVersion=4.9300;CDN=http://dus01.ps3.update.playstation.net/update/ps3/image/us/2026_0318_a2b60b6ac1d2e49e230144345616927c/PS3PATCH.PUP;CDN_Timeout=30;
Dest=84;ImageVersion=00010b94;SystemSoftwareVersion=4.9300;CDN=http://dus01.ps3.update.playstation.net/update/ps3/image/us/2026_0318_a2b60b6ac1d2e49e230144345616927c/PS3UPDAT.PUP;CDN_Timeout=30;
"""


def _make_pup(version: str, /, *, file_count: int | None = None) -> bytes:
    version_blob = f'{version}\n'.encode()
    entries = [(0x100, 48 + 2 * 32, len(version_blob), 0), (0x101, 0, 0, 0)]
    header = struct.pack('>8sQQQQQ', b'SCEUF\0\0\0', 1, 1, file_count or len(entries), 0, 0)
    return header + b''.join(struct.pack('>QQQQ', *entry) for entry in entries) + version_blob + b'\0' * 1024


@pytest.fixture(autouse=True)
def paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    bios = tmp_path / 'bios'
    state = tmp_path / 'cache' / 'firmware-update'
    monkeypatch.setattr(firmware, 'BIOS', bios)
    monkeypatch.setattr(firmware, 'PUP_PATH', bios / 'PS3UPDAT.PUP')
    monkeypatch.setattr(firmware, '_PART_PATH', bios / '.PS3UPDAT.PUP.part')
    monkeypatch.setattr(firmware, '_STATE_DIR', state)
    monkeypatch.setattr(firmware, '_CHECKED_PATH', state / 'checked')
    monkeypatch.setattr(firmware, '_PENDING_PATH', state / 'pending')
    return tmp_path


def test_pup_version(tmp_path: Path) -> None:
    pup = tmp_path / 'PS3UPDAT.PUP'
    pup.write_bytes(_make_pup('4.93'))
    assert firmware.pup_version(pup) == Decimal('4.93')


@pytest.mark.parametrize('content', [b'', b'not a pup file' * 10], ids=['empty', 'garbage'])
def test_pup_version_invalid(tmp_path: Path, content: bytes) -> None:
    pup = tmp_path / 'PS3UPDAT.PUP'
    pup.write_bytes(content)
    assert firmware.pup_version(pup) is None


def test_pup_version_caps_file_count(tmp_path: Path) -> None:
    pup = tmp_path / 'PS3UPDAT.PUP'
    pup.write_bytes(_make_pup('4.93', file_count=2**62))
    assert firmware.pup_version(pup) == Decimal('4.93')


def test_pup_version_missing(tmp_path: Path) -> None:
    assert firmware.pup_version(tmp_path / 'missing.PUP') is None


def test_installed_version(tmp_path: Path) -> None:
    version_txt = tmp_path / 'dev_flash' / 'vsh' / 'etc' / 'version.txt'
    version_txt.parent.mkdir(parents=True)
    version_txt.write_text('release:04.9300:\nbuild:68372,20221214:tetsu@tetsu-linux17\n')
    assert firmware.installed_version(tmp_path) == Decimal('4.93')
    assert firmware.installed_version(tmp_path / 'missing') is None


def test_parse_update_list() -> None:
    release = firmware.parse_update_list(_UPDATE_LIST)
    assert release is not None
    assert release.version == Decimal('4.93')
    assert release.url.endswith('/PS3UPDAT.PUP')
    assert firmware.parse_update_list('# US\n') is None


def _install(config_dir: Path, version: str, /) -> None:
    version_txt = config_dir / 'dev_flash' / 'vsh' / 'etc' / 'version.txt'
    version_txt.parent.mkdir(parents=True)
    version_txt.write_text(f'release:{version}:\n')


def _write_pending(url: str, /) -> None:
    firmware._STATE_DIR.mkdir(parents=True, exist_ok=True)
    firmware._PENDING_PATH.write_text(f'4.9300 {url}\n')


async def test_check_resumes_pending(tmp_path: Path) -> None:
    _write_pending('http://example.invalid/PS3UPDAT.PUP')
    firmware._CHECKED_PATH.touch()

    async with aiohttp.ClientSession() as session:
        assert await firmware.check(session, tmp_path) == firmware.Release(
            Decimal('4.93'), 'http://example.invalid/PS3UPDAT.PUP'
        )


async def test_check_drops_stale_pending(tmp_path: Path) -> None:
    _install(tmp_path, '04.9300')
    _write_pending('http://example.invalid/PS3UPDAT.PUP')
    firmware.PUP_PATH.parent.mkdir(parents=True)
    firmware._PART_PATH.write_bytes(b'partial')
    firmware._CHECKED_PATH.touch()

    async with aiohttp.ClientSession() as session:
        assert await firmware.check(session, tmp_path) is None

    assert not firmware._PENDING_PATH.exists()
    assert not firmware._PART_PATH.exists()


async def test_check_skips_within_interval(tmp_path: Path) -> None:
    firmware._STATE_DIR.mkdir(parents=True)
    firmware._CHECKED_PATH.touch()

    async with aiohttp.ClientSession() as session:
        assert await firmware.check(session, tmp_path) is None


@pytest.fixture
async def pup_server(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[tuple[BaseTestServer, bytes]]:
    pup = _make_pup('4.93')
    served = tmp_path / 'served.PUP'
    served.write_bytes(pup)

    async def file_handler(_: web.Request) -> web.FileResponse:
        return web.FileResponse(served)

    async def no_range_handler(_: web.Request) -> web.Response:
        return web.Response(body=pup)

    async def list_handler(request: web.Request) -> web.Response:
        url = request.url.with_path(f'/x_{hashlib.md5(pup).hexdigest()}/PS3UPDAT.PUP')
        return web.Response(text=f'Dest=84;ImageVersion=1;SystemSoftwareVersion=4.9300;CDN={url};CDN_Timeout=30;\n')

    app = web.Application()
    app.router.add_get('/norange/PS3UPDAT.PUP', no_range_handler)
    app.router.add_get('/list.txt', list_handler)
    app.router.add_get('/{name}/PS3UPDAT.PUP', file_handler)
    async with TestServer(app) as server:
        monkeypatch.setattr(firmware, '_UPDATE_LIST_URL', str(server.make_url('/list.txt')))
        yield server, pup


def _release(server: BaseTestServer, path: str, /) -> firmware.Release:
    return firmware.Release(Decimal('4.93'), str(server.make_url(path)))


async def test_check_reads_update_list(pup_server: tuple[BaseTestServer, bytes], tmp_path: Path) -> None:
    server, _ = pup_server
    _install(tmp_path, '04.9000')

    async with aiohttp.ClientSession() as session:
        release = await firmware.check(session, tmp_path)

    assert release is not None
    assert release.version == Decimal('4.93')
    assert release.url.startswith(str(server.make_url('/')))
    assert firmware._CHECKED_PATH.exists()
    assert firmware._PENDING_PATH.exists()


async def test_check_up_to_date(pup_server: tuple[BaseTestServer, bytes], tmp_path: Path) -> None:
    _install(tmp_path, '04.9300')

    async with aiohttp.ClientSession() as session:
        assert await firmware.check(session, tmp_path) is None

    assert not firmware._PENDING_PATH.exists()


async def test_update_downloads_pup(pup_server: tuple[BaseTestServer, bytes], tmp_path: Path) -> None:
    _, pup = pup_server
    _install(tmp_path, '04.9000')

    async with aiohttp.ClientSession() as session:
        await firmware.update(session, tmp_path)

    assert firmware.PUP_PATH.read_bytes() == pup
    assert not firmware._PENDING_PATH.exists()


@pytest.mark.parametrize('path', ['/x/PS3UPDAT.PUP', '/norange/PS3UPDAT.PUP'], ids=['range', 'range-ignored'])
async def test_download_resumes_part(pup_server: tuple[BaseTestServer, bytes], path: str) -> None:
    server, pup = pup_server
    firmware.PUP_PATH.parent.mkdir(parents=True)
    firmware._PART_PATH.write_bytes(pup[:100])
    progress: list[int] = []

    async def record(percent: int) -> None:
        progress.append(percent)

    async with aiohttp.ClientSession() as session:
        await firmware.download(
            session, _release(server, path.replace('/x/', f'/x_{hashlib.md5(pup).hexdigest()}/')), record
        )

    assert firmware.PUP_PATH.read_bytes() == pup
    assert not firmware._PART_PATH.exists()
    assert progress[-1] == 100


async def test_download_complete_part(pup_server: tuple[BaseTestServer, bytes]) -> None:
    server, pup = pup_server
    firmware.PUP_PATH.parent.mkdir(parents=True)
    firmware._PART_PATH.write_bytes(pup)

    async with aiohttp.ClientSession() as session:
        await firmware.download(session, _release(server, f'/x_{hashlib.md5(pup).hexdigest()}/PS3UPDAT.PUP'))

    assert firmware.PUP_PATH.read_bytes() == pup


async def test_download_rejects_md5_mismatch(pup_server: tuple[BaseTestServer, bytes]) -> None:
    server, _ = pup_server
    firmware.PUP_PATH.parent.mkdir(parents=True)
    firmware.PUP_PATH.write_bytes(b'old')
    _write_pending('http://example.invalid/PS3UPDAT.PUP')

    async with aiohttp.ClientSession() as session:
        with pytest.raises(ValueError, match='failed verification'):
            await firmware.download(session, _release(server, f'/x_{"0" * 32}/PS3UPDAT.PUP'))

    assert firmware.PUP_PATH.read_bytes() == b'old'
    assert not firmware._PART_PATH.exists()
    assert not firmware._PENDING_PATH.exists()


async def test_download_client_error_clears_state(pup_server: tuple[BaseTestServer, bytes]) -> None:
    server, _ = pup_server
    firmware.PUP_PATH.parent.mkdir(parents=True)
    firmware._PART_PATH.write_bytes(b'partial')
    _write_pending('http://example.invalid/PS3UPDAT.PUP')

    async with aiohttp.ClientSession() as session:
        with pytest.raises(aiohttp.ClientResponseError):
            await firmware.download(session, _release(server, '/missing.PUP'))

    assert not firmware._PART_PATH.exists()
    assert not firmware._PENDING_PATH.exists()
