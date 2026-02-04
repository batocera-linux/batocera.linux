from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, NotRequired, cast
from typing_extensions import TypedDict

from batocera_es_system.es_systems import load_es_systems
from batocera_es_system.registry import EmulatorInfo, EmulatorsBySystemMapping, EmulatorsMetadataMapping, Registry
from batocera_es_system.shared import (
    MISSING,
    ConfiggenDefaults,
    SystemDict,
    SystemsData,
    get_deep_value,
    safe_load_yaml,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


class _CoreExplanationsDict(TypedDict):
    flags: NotRequired[list[str]]
    explanation: NotRequired[str]


type _EmulatorExplanationsDict = dict[str, _CoreExplanationsDict]
type _SystemExplanationsDict = dict[str, _EmulatorExplanationsDict]
type _ArchExplanationsDict = dict[str, _SystemExplanationsDict]
type _ExplanationsDict = dict[str, _ArchExplanationsDict]


class _ResultCoreDict(TypedDict):
    enabled: bool
    explanation: str | None
    flags: NotRequired[list[str]]
    default: NotRequired[bool]


class _EmulatorsResultDict(TypedDict):
    name: str
    nb_variants: int
    nb_all_variants: int
    nb_explanations: int
    nb_all_explanations: int
    emulators: dict[str, dict[str, _ResultCoreDict]]
    red_flag: NotRequired[bool]


class _SortedListEncoder(json.JSONEncoder):
    def encode(self, o: Any) -> str:
        def sort_lists(item: Any) -> Any:
            if isinstance(item, list):
                return sorted(sort_lists(i) for i in cast('list[Any]', item))
            if isinstance(item, dict):
                return {k: sort_lists(v) for k, v in cast('dict[str, Any]', item.items())}
            return item

        return super().encode(sort_lists(o))


def _has_red_flag(nb_variants: int, nb_explanations: int, nb_all_explanations: int, /) -> bool:
    if nb_variants == 0 and nb_all_explanations == 0:
        return True
    if nb_variants == 0 and nb_all_explanations >= 1:
        return False
    if nb_variants == 1:
        return False
    return nb_variants != nb_explanations


def _get_boards_from_config(config_file: Path, /) -> list[str]:
    with config_file.open() as fp:
        for line in fp:
            m = re.search('^([^ ]+)=[ ]*(.*)[ ]*$', line)
            if m and m.group(1) == 'BR2_TARGET_BATOCERA_IMAGES':
                dirs = m.group(2)[1:-1].split(' ')
                return [Path(dir).name for dir in dirs]

    return []


def _generate_target_system_report(
    target: str,
    system_name: str,
    system_data: SystemDict,
    explanations: _ExplanationsDict,
    configgen_defaults: ConfiggenDefaults,
    emulators_metadata: EmulatorsMetadataMapping,
    all_system_emulators: Mapping[str, Mapping[str, EmulatorInfo]],
    /,
) -> _EmulatorsResultDict | None:
    nb_variants = 0
    nb_all_variants = 0
    nb_explanations = 0
    nb_all_explanations = 0
    default_found = False

    emulators_result: dict[str, dict[str, _ResultCoreDict]] = {}

    for emulator_name, emulators_by_core in sorted(all_system_emulators.items()):
        cores_report: dict[str, _ResultCoreDict] = {}
        cores_metadata = emulators_metadata.get(emulator_name, {})

        for core_name, _ in sorted(emulators_by_core.items()):
            core_metadata = cores_metadata.get(core_name)
            nb_all_variants += 1

            arch_explanation = get_deep_value(
                explanations, target, system_name, emulator_name, core_name, 'explanation'
            )
            default_explanation = get_deep_value(
                explanations, 'default', system_name, emulator_name, core_name, 'explanation'
            )

            explanation = (
                arch_explanation
                if arch_explanation is not MISSING
                else (default_explanation if default_explanation is not MISSING else None)
            )

            core_report = cores_report[core_name] = {
                'enabled': bool(core_metadata),
                'explanation': explanation,
            }

            if core_metadata:
                nb_variants += 1

                if explanation is not None:
                    nb_explanations += 1

                flags = []
                if (
                    arch_flags := get_deep_value(explanations, target, system_name, emulator_name, core_name, 'flags')
                ) is not MISSING:
                    flags += arch_flags
                if (
                    default_flags := get_deep_value(
                        explanations, 'default', system_name, emulator_name, core_name, 'flags'
                    )
                ) is not MISSING:
                    flags += default_flags

                core_report['flags'] = flags

                if core_metadata['default']:
                    default_found = True

                core_report['default'] = core_metadata['default']
            elif explanation is not None:
                nb_all_explanations += 1

        emulators_result[emulator_name] = cores_report

    if not emulators_result:
        return None

    if nb_variants > 0 and not default_found:
        default_emulator = configgen_defaults.get(system_name, 'emulator')
        default_core = configgen_defaults.get(system_name, 'core')

        raise Exception(f'default core ({default_emulator}/{default_core}) not enabled for {target}/{system_name}')

    return {
        'name': system_data['name'],
        'nb_variants': nb_variants,
        'nb_all_variants': nb_all_variants,
        'nb_explanations': nb_explanations,
        'nb_all_explanations': nb_all_explanations,
        'emulators': emulators_result,
        'red_flag': _has_red_flag(nb_variants, nb_explanations, nb_all_explanations),
    }


def _generate_target_report(
    target_dir: Path,
    es_systems_data: SystemsData,
    explanations: _ExplanationsDict,
    configgen_dir: Path,
    all_emulators_by_system: EmulatorsBySystemMapping,
    /,
) -> dict[str, _EmulatorsResultDict]:
    target = target_dir.name

    registry = Registry.load_path_file(target_dir / 'info_files.txt')
    configgen_defaults = ConfiggenDefaults.for_defaults(
        configgen_dir / 'configgen-defaults.yml', configgen_dir / f'configgen-defaults-{target}.yml'
    )
    systems_metadata = registry.get_systems_metadata(configgen_defaults)

    return {
        system_name: target_system_report
        for system_name, system_data in es_systems_data.items()
        if (
            target_system_report := _generate_target_system_report(
                target,
                system_name,
                system_data,
                explanations,
                configgen_defaults,
                systems_metadata.get(system_name, {}),
                all_emulators_by_system.get(system_name, {}),
            )
        )
        is not None
    }


def _generate_systems_report(
    reports_data_dir: Path, es_systems_yml: Path, explanations_yml: Path, configgen_dir: Path, output_file: Path, /
) -> None:
    results: dict[str, dict[str, _EmulatorsResultDict]] = {}
    explanations = safe_load_yaml(explanations_yml, '_ExplanationsDict')
    es_systems_data = load_es_systems(es_systems_yml)
    all_emulators = Registry.load_path_file(reports_data_dir / 'all_info_files.txt')
    all_emulators_by_system = all_emulators.emulators_by_system

    for target_dir in reports_data_dir.iterdir():
        if not target_dir.is_dir():
            continue

        target_systems = _generate_target_report(
            target_dir, es_systems_data, explanations, configgen_dir, all_emulators_by_system
        )

        for board in _get_boards_from_config(target_dir / '.config'):
            results[board] = target_systems

    output_file.write_text(json.dumps(results, indent=2, sort_keys=True, cls=_SortedListEncoder))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('reports_data_dir', type=Path, help='Directory containing reports data directories')
    parser.add_argument('es_systems_yml', type=Path, help='es_systems.yml definition file')
    parser.add_argument('explanations_yml', type=Path, help='explanations.yml definition file')
    parser.add_argument('configgen_dir', type=Path, help='Path to configgen configs directory')
    parser.add_argument('dest', type=Path, help='Output file')

    args = parser.parse_args()

    _generate_systems_report(
        args.reports_data_dir, args.es_systems_yml, args.explanations_yml, args.configgen_dir, args.dest
    )
