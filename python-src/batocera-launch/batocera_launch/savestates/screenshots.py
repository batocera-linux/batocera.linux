# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

from __future__ import annotations

import struct
import zipfile
import zlib
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

_DUCKSTATION_MAGIC: Final = 0x43435544


def encode_png(width: int, height: int, rgba: bytes, /) -> bytes:
    rgb = bytearray(width * height * 3)
    for channel in range(3):
        rgb[channel::3] = rgba[channel : width * height * 4 : 4]

    stride = width * 3
    rows = b''.join(b'\0' + rgb[row * stride : (row + 1) * stride] for row in range(height))

    def chunk(tag: bytes, data: bytes, /) -> bytes:
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data))

    return b''.join(
        (
            b'\x89PNG\r\n\x1a\n',
            chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)),
            chunk(b'IDAT', zlib.compress(rows)),
            chunk(b'IEND', b''),
        )
    )


def duckstation_screenshot(path: Path, /) -> bytes | None:
    with path.open('rb') as state:
        header = state.read(200)
        if len(header) < 200:
            return None

        magic, version = struct.unpack_from('<II', header)
        compression, width, height, size, offset = struct.unpack_from('<5I', header, 180)
        if magic != _DUCKSTATION_MAGIC or not width or not height:
            return None

        # compressed screenshots came with version 69
        if version < 69:
            compression, size = 0, width * height * 4

        state.seek(offset)
        data = state.read(size)

    match compression:
        case 0:
            pixels = data
        case 1:
            pixels = zlib.decompress(data)
        case 2:
            try:
                from compression import zstd
            except ImportError:
                return None
            pixels = zstd.decompress(data)
        case _:
            return None

    if len(pixels) < width * height * 4:
        return None

    return encode_png(width, height, pixels)


def pcsx2_screenshot(path: Path, /) -> bytes | None:
    try:
        with zipfile.ZipFile(path) as state:
            return state.read('Screenshot.png')
    except OSError, KeyError, zipfile.BadZipFile:
        return None


SCREENSHOTS: Final[dict[str, Callable[[Path], bytes | None]]] = {
    'duckstation': duckstation_screenshot,
    'pcsx2': pcsx2_screenshot,
}
