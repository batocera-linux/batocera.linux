from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from batocera_common.yaml import safe_load_yaml
from batocera_es_system.shared import (
    SystemDict,
    SystemsData,
    SystemsDataMapping,
    peekable,
    protect_xml,
    to_xml_attribute,
    wrap_tag,
    write_xml,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from pathlib import Path

    from batocera_es_system.registry import (
        SystemMetadata,
        SystemsMetadataMapping,
    )


_DEFAULT_PARENTPATH: Final = '/userdata/roms'
_DEFAULT_COMMAND: Final = 'batocera-launch %CONTROLLERSCONFIG% -system %SYSTEM% -rom %ROM% -gameinfoxml %GAMEINFOXML% -systemname %SYSTEMNAME%'


def _file_extensions_to_xml(values: Iterable[str], /) -> str:
    return ' '.join(f'.{value}'.lower() for value in sorted(values) if value)


def _emulators_data_to_xml(system_metadata: SystemMetadata | None, /) -> Iterator[str]:
    if not system_metadata:
        return

    def _inner_emulators_data_to_xml() -> Iterator[str]:
        for emulator, cores in sorted(system_metadata.emulators.items(), key=lambda x: x[0]):
            if not cores:
                continue

            yield f'            <emulator name="{emulator}">'
            yield '                <cores>'

            for core, core_data in sorted(cores.items(), key=lambda x: x[0]):
                incompatible_extensions = ''
                if file_extensions := core_data.file_extensions:
                    incompatible_extensions = to_xml_attribute(
                        'incompatible_extensions',
                        _file_extensions_to_xml(system_metadata.file_extensions - file_extensions),
                    )

                default_attribute = ' default="true"' if core_data.default else ''

                yield f'                    <core{default_attribute}{incompatible_extensions}>{core}</core>'

            yield '                </cores>'
            yield '            </emulator>'

    yield from wrap_tag('emulators', _inner_emulators_data_to_xml(), indent='        ')


def _system_dict_to_xml(
    name: str,
    data: SystemDict,
    system_metadata: SystemMetadata | None,
    included_systems: set[str],
    /,
) -> Iterator[str]:
    emulator_strings = peekable(_emulators_data_to_xml(system_metadata))

    if not emulator_strings and not data.get('force'):
        return

    path = data.get('path', name)
    if path is None:
        path = ''
    elif not path.startswith('/'):
        path = f'{_DEFAULT_PARENTPATH}/{path}'

    platform = data.get('platform', name) or ''
    file_extensions = _file_extensions_to_xml(
        system_metadata.file_extensions if system_metadata else data.get('file_extensions', [])
    )
    group = data.get('group', '') or ''
    command = data.get('command', _DEFAULT_COMMAND)

    yield '  <system>'
    yield f'        <fullname>{protect_xml(data["name"])}</fullname>'
    yield f'        <name>{name}</name>'
    yield f'        <manufacturer>{protect_xml(data["manufacturer"])}</manufacturer>'
    yield f'        <release>{protect_xml(data["release"])}</release>'
    yield f'        <hardware>{protect_xml(data["hardware"])}</hardware>'

    if file_extensions:
        if path:
            yield f'        <path>{path}</path>'
        yield f'        <extension>{file_extensions}</extension>'
        yield f'        <command>{command}</command>'

    if platform:
        yield f'        <platform>{protect_xml(platform)}</platform>'

    yield f'        <theme>{data.get("theme", name)}</theme>'

    if group:
        yield f'        <group>{protect_xml(group)}</group>'

    yield from emulator_strings

    yield '  </system>'

    included_systems.add(name)


def _systems_data_to_xml(
    systems_data: SystemsDataMapping,
    system_core_data: SystemsMetadataMapping,
    included_systems: set[str],
    /,
) -> Iterator[str]:
    for system_name, system_data in systems_data.items():
        yield from _system_dict_to_xml(
            system_name,
            system_data,
            system_core_data.get(system_name),
            included_systems,
        )


def load_es_systems(es_systems_yml: Path, /) -> SystemsData:
    systems_data = safe_load_yaml(es_systems_yml, SystemsData) or {}
    return dict(sorted(systems_data.items(), key=lambda x: x[0]))


@dataclass(slots=True, frozen=True)
class BuiltSystem:
    system: SystemDict
    metadata: SystemMetadata | None


type BuiltSystems = dict[str, BuiltSystem]
type BuiltSystemsMapping = Mapping[str, BuiltSystem]


def build(
    systems_core_metadata: SystemsMetadataMapping,
    es_systems_yml: Path,
    output_dir: Path,
    /,
) -> BuiltSystems:
    systems_data = load_es_systems(es_systems_yml)
    included_systems: set[str] = set()

    es_systems_path = output_dir / 'es_systems.cfg'

    print(f'Generating {es_systems_path}...')

    write_xml(
        es_systems_path,
        'systemList',
        _systems_data_to_xml(systems_data, systems_core_metadata, included_systems),
    )

    return {
        name: BuiltSystem(system=data, metadata=systems_core_metadata.get(name))
        for name, data in systems_data.items()
        if name in included_systems
    }
