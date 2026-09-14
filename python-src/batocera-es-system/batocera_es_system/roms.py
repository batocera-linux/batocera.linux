from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

from batocera_es_system.shared import peekable

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from pathlib import Path

    from batocera_es_system.es_systems import BuiltSystem, BuiltSystemsMapping


def _format_extensions(extensions: Iterable[str], /) -> str:
    return ' '.join(f'.{value}'.lower() for value in extensions if value)


def _get_extensions_strings(prefix: str, built_system: BuiltSystem, /) -> Iterator[str]:
    if built_system.metadata is None:
        yield f'{prefix}: {_format_extensions(built_system.system.get("extensions", []))}'
        return

    yield f'{prefix}:'
    yield from (
        f'- {core_name if emulator_name == core_name else f"{emulator_name}/{core_name}"}: {
            _format_extensions(sorted(core_metadata.file_extensions))
        }'
        for emulator_name, emulator in built_system.metadata.emulators.items()
        for core_name, core_metadata in emulator.items()
    )


def build(built_systems_data: BuiltSystemsMapping, roms_dir: Path, output: Path, /) -> None:
    target = output / 'roms'

    if target.is_dir() and peekable(target.iterdir()):
        print(f'Removing {target}...')
        shutil.rmtree(target)
        target.mkdir(parents=True)

    print(f'Generating {target}...')
    for system_name, built_system in built_systems_data.items():
        dir_name = built_system.system.get('path', system_name)

        if dir_name is None or dir_name.startswith('/'):
            continue  # nothing to do

        system_target = target / dir_name
        system_source = roms_dir / dir_name

        if not system_target.is_dir():
            if system_source.is_dir():
                shutil.copytree(system_source, system_target)
            else:
                system_target.mkdir(parents=True)

        lines: list[str] = [
            f'## SYSTEM {built_system.system["name"].upper()} ##',
            '-------------------------------------------------------------------------------',
            *_get_extensions_strings('ROM files extensions accepted', built_system),
        ]

        if 'comment_en' in built_system.system:
            lines.append(built_system.system['comment_en'])

        lines.extend(
            [
                '-------------------------------------------------------------------------------',
                *_get_extensions_strings('Extensions des fichiers ROMs permises', built_system),
            ]
        )

        if 'comment_fr' in built_system.system:
            lines.append(built_system.system['comment_fr'])

        system_target.joinpath('_info.txt').write_text('\n'.join(lines).strip() + '\n')
