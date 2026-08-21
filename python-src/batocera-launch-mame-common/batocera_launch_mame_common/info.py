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
