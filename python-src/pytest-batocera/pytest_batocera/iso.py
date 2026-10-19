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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


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


def write_ps2_disc(iso: Path, serial: str, /, *, elf_suffix: str = '', pad_first_sector: bool = False) -> Path:
    elf = f'{serial[:4]}_{serial[5:8]}.{serial[8:]}{elf_suffix};1'
    return _write_iso(iso, [b'DGO', b'DRIVERS', elf.encode(), b'SYSTEM.CNF;1'], pad_first_sector=pad_first_sector)
