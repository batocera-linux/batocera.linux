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
from xml.dom import minidom

from batocera_common.asyncio import run
from batocera_launch import BatoceraException

from .paths import MAME_BIN_DIR

if TYPE_CHECKING:
    from pathlib import Path


async def get_machine_size(machine: str, tmpdir: Path, /):
    try:
        result = await run(MAME_BIN_DIR / 'mame', '-listxml', machine, check=True, text=True)
    except Exception as e:
        raise BatoceraException(f'mame -listxml {machine} failed') from e

    info_file = tmpdir / 'infos.xml'
    info_file.write_text(result.stdout)

    info_dom = minidom.parse(str(info_file))
    display = info_dom.getElementsByTagName('display')

    for element in display:
        return (
            int(element.getAttribute('width')),
            int(element.getAttribute('height')),
            int(element.getAttribute('rotate')),
        )

    raise BatoceraException('Display element not found')
