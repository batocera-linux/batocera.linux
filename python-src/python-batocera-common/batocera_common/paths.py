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

from pathlib import Path
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from _typeshed import StrPath
    from collections.abc import Iterable, Iterator

BATOCERA_SHARE_DIR: Final = Path('/usr/share/batocera')
USERDATA: Final = Path('/userdata')

HOME: Final = USERDATA / 'system'
CONFIGS: Final = HOME / 'configs'
SAVES: Final = USERDATA / 'saves'
SCREENSHOTS: Final = USERDATA / 'screenshots'
RECORDINGS: Final = USERDATA / 'recordings'
BIOS: Final = USERDATA / 'bios'
OVERLAYS: Final = USERDATA / 'overlays'
CACHE: Final = HOME / 'cache'
ROMS: Final = USERDATA / 'roms'
CHEATS: Final = USERDATA / 'cheats'
LOGS: Final = HOME / 'logs'
BATOCERA_CONF: Final = HOME / 'batocera.conf'

SQUASHFS_DIR: Final = Path('/var/run/squashfs')
ROM_OVERLAY_DIR: Final = Path('/var/run/overlays')

SYSCONFIG: Final = BATOCERA_SHARE_DIR / 'sysconfigs' / 'batocera.conf'


def files_in_directories(filename: StrPath, directories: Iterable[Path], /) -> Iterator[Path]:
    """Yield the path to a file in each of the given directories."""

    for directory in directories:
        yield directory / filename


def existing_files_in_directories(filename: StrPath, directories: Iterable[Path], /) -> Iterator[Path]:
    for path in files_in_directories(filename, directories):
        if path.exists():
            yield path


def glob_in_directories(
    pattern: str, directories: Iterable[Path], /, *, case_sensitive: bool | None = None, recurse_symlinks: bool = False
) -> Iterator[Path]:
    """Yield the path to files matching a glob pattern in each of the given directories."""

    for directory in directories:
        yield from directory.glob(pattern, case_sensitive=case_sensitive, recurse_symlinks=recurse_symlinks)
