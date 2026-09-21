from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import uvloop
from pyfakefs import helpers
from pyfakefs.fake_filesystem import FakeFilesystem, OSType
from pyfakefs.fake_filesystem_unittest import Patcher

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Mapping
    from pathlib import Path
    from types import ModuleType

    from pytest_asyncio.plugin import LoopFactory


def pytest_asyncio_loop_factories(config: pytest.Config, item: pytest.Item) -> Mapping[str, LoopFactory]:
    return {
        'uvloop': uvloop.new_event_loop,
    }


@pytest.fixture
def fs_modules_to_reload() -> list[ModuleType] | None:
    return


@pytest.fixture
def fs(fs_modules_to_reload: list[ModuleType] | None, monkeypatch: pytest.MonkeyPatch) -> Iterator[FakeFilesystem]:
    with monkeypatch.context() as mp:
        # delete these so our fake filesystem does not inherit the temporary directory
        # of the machine running the tests
        mp.delenv('TMP', raising=False)
        mp.delenv('TMPDIR', raising=False)
        mp.delenv('TEMP', raising=False)

        # batocera runs as root
        helpers.set_uid(0)

        with Patcher(
            additional_skip_names=[
                'syrupy.utils',
                'syrupy.extensions.amber.serializer',
                'syrupy.extensions.image',
                'syrupy.extensions.single_file',
            ],
            modules_to_reload=fs_modules_to_reload,
            allow_root_user=True,
        ) as patcher:
            patcher.fs.os = OSType.LINUX  # pyright: ignore
            yield patcher.fs  # pyright: ignore

        helpers.reset_ids()


def _iso_directory_record(name: bytes, extent: int = 0) -> bytes:
    length = 33 + len(name) + (1 - len(name) % 2)
    record = bytearray(length)
    record[0] = length
    record[2:6] = extent.to_bytes(4, 'little')
    record[32] = len(name)
    record[33 : 33 + len(name)] = name
    return bytes(record)


def _write_iso(iso: Path, names: list[bytes], /, *, pad_first_sector: bool = False) -> Path:
    sector = 2048
    root_extent = 20
    records = [_iso_directory_record(b'\x00'), _iso_directory_record(b'\x01'), *map(_iso_directory_record, names)]
    if pad_first_sector:
        first = b''.join(records[:2])
        directory = first.ljust(sector, b'\x00') + b''.join(records[2:])
    else:
        directory = b''.join(records)

    pvd = bytearray(sector)
    pvd[0] = 1
    pvd[1:6] = b'CD001'
    pvd[156:190] = _iso_directory_record(b'\x00', root_extent)
    pvd[156 + 10 : 156 + 14] = len(directory).to_bytes(4, 'little')

    terminator = bytearray(sector)
    terminator[0] = 255
    terminator[1:6] = b'CD001'

    image = bytearray(root_extent * sector)
    image[16 * sector : 17 * sector] = pvd
    image[17 * sector : 18 * sector] = terminator
    image += directory

    iso.parent.mkdir(parents=True, exist_ok=True)
    iso.write_bytes(bytes(image))
    return iso


def _write_ps2_disc(iso: Path, serial: str, /, *, elf_suffix: str = '', pad_first_sector: bool = False) -> Path:
    elf = f'{serial[:4]}_{serial[5:8]}.{serial[8:]}{elf_suffix};1'
    return _write_iso(iso, [b'DGO', b'DRIVERS', elf.encode(), b'SYSTEM.CNF;1'], pad_first_sector=pad_first_sector)


@pytest.fixture
def write_ps2_disc() -> Callable[..., Path]:
    return _write_ps2_disc
