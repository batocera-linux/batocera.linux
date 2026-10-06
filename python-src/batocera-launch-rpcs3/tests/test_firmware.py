from __future__ import annotations

import hashlib
import struct
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

import aiohttp
import pytest
from batocera_launch_rpcs3 import firmware
from yarl import URL

from batocera_common.paths import CONFIGS

if TYPE_CHECKING:
    from aiointercept import aiointercept


pytestmark = pytest.mark.usefixtures('fs')

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


def test_pup_version() -> None:
    firmware.PUP_PATH.parent.mkdir(parents=True)
    firmware.PUP_PATH.write_bytes(_make_pup('4.93'))
    assert firmware.pup_version() == Decimal('4.93')


@pytest.mark.parametrize('content', [b'', b'not a pup file' * 10], ids=['empty', 'garbage'])
def test_pup_version_invalid(content: bytes) -> None:
    firmware.PUP_PATH.parent.mkdir(parents=True)
    firmware.PUP_PATH.write_bytes(content)
    assert firmware.pup_version() is None


def test_pup_version_caps_file_count() -> None:
    firmware.PUP_PATH.parent.mkdir(parents=True)
    firmware.PUP_PATH.write_bytes(_make_pup('4.93', file_count=2**62))
    assert firmware.pup_version() == Decimal('4.93')


def test_pup_version_missing() -> None:
    assert firmware.pup_version() is None


def test_installed_version() -> None:
    version_txt = CONFIGS / 'rpcs3' / 'dev_flash' / 'vsh' / 'etc' / 'version.txt'
    version_txt.parent.mkdir(parents=True)
    version_txt.write_text('release:04.9300:\nbuild:68372,20221214:tetsu@tetsu-linux17\n')
    assert firmware.installed_version(CONFIGS / 'rpcs3') == Decimal('4.93')
    assert firmware.installed_version(CONFIGS / 'missing') is None


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


@pytest.mark.usefixtures('pup_interceptor')
async def test_check_resumes_pending() -> None:
    _write_pending('http://example.invalid/PS3UPDAT.PUP')
    firmware._CHECKED_PATH.touch()

    async with aiohttp.ClientSession() as session:
        assert await firmware.check(session, CONFIGS / 'rpcs3') == firmware.Release(
            Decimal('4.93'), 'http://example.invalid/PS3UPDAT.PUP'
        )


@pytest.mark.usefixtures('pup_interceptor')
async def test_check_drops_stale_pending() -> None:
    _install(CONFIGS / 'rpcs3', '04.9300')
    _write_pending('http://example.invalid/PS3UPDAT.PUP')
    firmware.PUP_PATH.parent.mkdir(parents=True)
    firmware._PART_PATH.write_bytes(b'partial')
    firmware._CHECKED_PATH.touch()

    async with aiohttp.ClientSession() as session:
        assert await firmware.check(session, CONFIGS / 'rpcs3') is None

    assert not firmware._PENDING_PATH.exists()
    assert not firmware._PART_PATH.exists()


@pytest.mark.usefixtures('pup_interceptor')
async def test_check_skips_within_interval() -> None:
    firmware._STATE_DIR.mkdir(parents=True)
    firmware._CHECKED_PATH.touch()

    async with aiohttp.ClientSession() as session:
        assert await firmware.check(session, CONFIGS / 'rpcs3') is None


@pytest.fixture
def pup(pup_version: str = '4.93') -> bytes:
    return _make_pup(pup_version)


@pytest.fixture
def pup_url(pup: bytes) -> URL:
    return URL(
        f'http://dus01.ps3.update.playstation.net/update/ps3/image/us/x_{hashlib.md5(pup).hexdigest()}/PS3UPDAT.PUP'
    )


@pytest.fixture
async def pup_interceptor(mock_server: aiointercept, pup: bytes, pup_url: URL) -> None:
    served = Path('/tmp') / 'served.PUP'
    served.write_bytes(pup)

    mock_server.get(
        firmware._UPDATE_LIST_URL,
        status=200,
        body=f'Dest=84;ImageVersion=1;SystemSoftwareVersion=4.9300;CDN={pup_url};CDN_Timeout=30;\n',
    )
    mock_server.get(pup_url, status=200, body=pup)
    mock_server.get(pup_url.parent.parent / f'x_{"0" * 32}' / 'PS3UPDAT.PUP', status=200, body=pup)
    mock_server.get(pup_url.with_path('norange/PS3UPDAT.PUP'), status=200, body=pup)
    mock_server.get(pup_url.with_path('missing.PUP'), status=404)


def _release(url: URL, /) -> firmware.Release:
    return firmware.Release(Decimal('4.93'), str(url))


@pytest.mark.usefixtures('pup_interceptor')
async def test_check_reads_update_list() -> None:
    _install(CONFIGS / 'rpcs3', '04.9000')

    async with aiohttp.ClientSession() as session:
        release = await firmware.check(session, CONFIGS / 'rpcs3')

    assert release is not None
    assert release.version == Decimal('4.93')
    assert release.url.startswith('http://dus01.ps3.update.playstation.net/update/ps3/image/us')
    assert firmware._CHECKED_PATH.exists()
    assert firmware._PENDING_PATH.exists()


@pytest.mark.usefixtures('pup_interceptor')
async def test_check_up_to_date() -> None:
    _install(CONFIGS / 'rpcs3', '04.9300')

    async with aiohttp.ClientSession() as session:
        assert await firmware.check(session, CONFIGS / 'rpcs3') is None

    assert not firmware._PENDING_PATH.exists()


@pytest.mark.usefixtures('pup_interceptor')
async def test_update_downloads_pup(pup: bytes) -> None:
    _install(CONFIGS / 'rpcs3', '04.9000')

    async with aiohttp.ClientSession() as session:
        await firmware.update(session, CONFIGS / 'rpcs3')

    assert firmware.PUP_PATH.read_bytes() == pup
    assert not firmware._PENDING_PATH.exists()


@pytest.mark.usefixtures('pup_interceptor')
@pytest.mark.parametrize('path', [None, 'norange/PS3UPDAT.PUP'], ids=['range', 'range-ignored'])
async def test_download_resumes_part(pup: bytes, pup_url: URL, path: str | None) -> None:
    firmware.PUP_PATH.parent.mkdir(parents=True)
    firmware._PART_PATH.write_bytes(pup[:100])
    progress: list[int] = []

    async def record(percent: int) -> None:
        progress.append(percent)

    async with aiohttp.ClientSession() as session:
        await firmware.download(
            session,
            _release(pup_url if path is None else pup_url.with_path(path)),
            record,
        )

    assert firmware.PUP_PATH.read_bytes() == pup
    assert not firmware._PART_PATH.exists()
    assert progress[-1] == 100


@pytest.mark.usefixtures('pup_interceptor')
async def test_download_complete_part(pup: bytes, pup_url: URL) -> None:
    firmware.PUP_PATH.parent.mkdir(parents=True)
    firmware._PART_PATH.write_bytes(pup)

    async with aiohttp.ClientSession() as session:
        await firmware.download(session, _release(pup_url))

    assert firmware.PUP_PATH.read_bytes() == pup


@pytest.mark.usefixtures('pup_interceptor')
async def test_download_rejects_md5_mismatch(pup_url: URL) -> None:
    firmware.PUP_PATH.parent.mkdir(parents=True)
    firmware.PUP_PATH.write_bytes(b'old')
    _write_pending('http://example.invalid/PS3UPDAT.PUP')

    async with aiohttp.ClientSession() as session:
        with pytest.raises(ValueError, match='failed verification'):
            await firmware.download(
                session,
                _release(pup_url.parent.parent / f'x_{"0" * 32}' / 'PS3UPDAT.PUP'),
            )

    assert firmware.PUP_PATH.read_bytes() == b'old'
    assert not firmware._PART_PATH.exists()
    assert not firmware._PENDING_PATH.exists()


@pytest.mark.usefixtures('pup_interceptor')
async def test_download_client_error_clears_state(pup_url: URL) -> None:
    firmware.PUP_PATH.parent.mkdir(parents=True)
    firmware._PART_PATH.write_bytes(b'partial')
    _write_pending('http://example.invalid/PS3UPDAT.PUP')

    async with aiohttp.ClientSession() as session:
        with pytest.raises(aiohttp.ClientResponseError):
            await firmware.download(session, _release(pup_url.with_path('missing.PUP')))

    assert not firmware._PART_PATH.exists()
    assert not firmware._PENDING_PATH.exists()
