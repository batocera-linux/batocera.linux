from __future__ import annotations

import shutil
from typing import TYPE_CHECKING, Literal

from batocera_es_system.shared import SystemDict, SystemsDataMapping, peekable

if TYPE_CHECKING:
    from pathlib import Path


def _get_comment(data: SystemDict, key: Literal['comment_en', 'comment_fr'], /) -> str:
    if key in data:
        return f'{data[key]}\n'

    return ''


def build(systems_data: SystemsDataMapping, roms_dir: Path, output: Path, /) -> None:
    target = output / 'roms'

    if target.is_dir() and peekable(target.iterdir()):
        print(f'Removing {target}...')
        shutil.rmtree(target)
        target.mkdir(parents=True)

    print(f'Generating {target}...')
    for system_name, system in systems_data.items():
        dir_name = system.get('path', system_name)

        if dir_name is None or dir_name.startswith('/'):
            continue  # nothing to do

        system_target = target / dir_name
        system_source = roms_dir / dir_name

        if not system_target.is_dir():
            if system_source.is_dir():
                shutil.copytree(system_source, system_target)
            else:
                system_target.mkdir(parents=True)

        extensions = ' '.join(f'.{value}'.lower() for value in system['extensions'] if value)

        (system_target / '_info.txt').write_text(f"""## SYSTEM {system['name'].upper()} ##
-------------------------------------------------------------------------------
ROM files extensions accepted: "{extensions}"{_get_comment(system, 'comment_en')}
-------------------------------------------------------------------------------
Extensions des fichiers ROMs permises: "{extensions}"{_get_comment(system, 'comment_fr')}
""")
