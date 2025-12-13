#
# - Generates the es_systems.cfg file
# - Generates roms folder and emulators folders
# - Generate the _info.txt file with the emulator information
# - Information from the emulators are being extracted from the file es_system.yml
#

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, NotRequired, cast
from typing_extensions import TypedDict

from batocera_es_system_shared import (
    MISSING,
    CoreDict,
    DefaultDict,
    SystemDict,
    get_deep_value,
    is_arch_valid,
    is_valid_requirements,
    safe_load_yaml,
)


class _ConfigDict(TypedDict, extra_items=int):
    BR2_TARGET_BATOCERA_IMAGES: NotRequired[str]


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


def _find_boards_from_config(config: _ConfigDict, /) -> list[str]:
    if 'BR2_TARGET_BATOCERA_IMAGES' not in config:
        return []
    dirs = config['BR2_TARGET_BATOCERA_IMAGES'][1:-1].split(' ')
    return [Path(dir).name for dir in dirs]


def _load_config(config_file: Path, /) -> _ConfigDict:
    config: _ConfigDict = {}
    with config_file.open() as fp:
        for line in fp:
            m = re.search('^([^ ]+)=[ ]*(.*)[ ]*$', line)
            if m:
                if m.group(2) == 'y':
                    config[m.group(1)] = 1
                else:
                    config[m.group(1)] = m.group(2)
    return config


def _list_emulators(
    arch: str,
    system: str,
    data: SystemDict,
    explanations_yaml: _ExplanationsDict,
    config: _ConfigDict,
    default_emulator: str | None,
    default_core: str | None,
    /,
) -> _EmulatorsResultDict:
    emulators_result: dict[str, dict[str, _ResultCoreDict]] = {}
    nb_variants = 0
    nb_all_variants = 0
    nb_explanations = 0
    nb_all_explanations = 0

    default_found = False

    emulators = data.get('emulators', {})

    for emulator, emulator_data in sorted(emulators.items(), key=lambda item: item[0]):
        if not is_arch_valid(arch, emulator_data):
            continue

        result_cores: dict[str, _ResultCoreDict] = {}

        core_keys = [key for key in emulator_data if key not in ['archs_include', 'archs_exclude']]

        for core in sorted(core_keys):
            core_data = cast('CoreDict', emulator_data[core])
            result_core = result_cores[core] = {
                'enabled': False,
                'explanation': None,
            }
            nb_all_variants += 1

            if (
                'requireAnyOf' in core_data
                and is_valid_requirements(config, core_data['requireAnyOf'])
                and is_arch_valid(arch, core_data)
            ):
                result_core['enabled'] = True
                nb_variants += 1

                # tell why this core is selected
                if (
                    arch_explanation := get_deep_value(explanations_yaml, arch, system, emulator, core, 'explanation')
                ) is not MISSING:
                    result_core['explanation'] = arch_explanation
                    nb_explanations += 1
                elif (
                    default_explanation := get_deep_value(
                        explanations_yaml, 'default', system, emulator, core, 'explanation'
                    )
                ) is not MISSING:
                    result_core['explanation'] = default_explanation
                    nb_explanations += 1
                else:
                    result_core['explanation'] = None

                # flags - flags are cumulative
                set_flags = []
                if (
                    arch_flags := get_deep_value(explanations_yaml, arch, system, emulator, core, 'flags')
                ) is not MISSING:
                    set_flags += arch_flags
                if (
                    default_flags := get_deep_value(explanations_yaml, 'default', system, emulator, core, 'flags')
                ) is not MISSING:
                    set_flags += default_flags
                result_core['flags'] = set_flags

                # default or not
                if emulator == default_emulator and core == default_core:
                    result_core['default'] = True
                    default_found = True
                else:
                    result_core['default'] = False
            else:
                # explanations tell why a core is not enabled too
                result_core['enabled'] = False
                if (
                    arch_explanation := get_deep_value(explanations_yaml, arch, system, emulator, core, 'explanation')
                ) is not MISSING:
                    result_core['explanation'] = arch_explanation
                    nb_all_explanations += 1
                elif (
                    default_explanation := get_deep_value(
                        explanations_yaml, 'default', system, emulator, core, 'explanation'
                    )
                ) is not MISSING:
                    result_core['explanation'] = default_explanation
                    nb_all_explanations += 1
                else:
                    result_core['explanation'] = None

        emulators_result[emulator] = result_cores

    if nb_variants > 0 and not default_found:
        raise Exception(f'default core ({default_emulator}/{default_core}) not enabled for {arch}/{system}')

    return {
        'name': data['name'],
        'nb_variants': nb_variants,
        'nb_all_variants': nb_all_variants,
        'nb_explanations': nb_explanations,
        'nb_all_explanations': nb_all_explanations,
        'emulators': emulators_result,
    }


def _generate_report(rules_yaml: Path, explanations_yaml: Path, configs_dir: Path, defaults_dir: Path, /) -> None:
    rules = safe_load_yaml(rules_yaml, 'dict[str, SystemDict]')
    explanations = safe_load_yaml(explanations_yaml, '_ExplanationsDict')
    result_archs: dict[str, dict[str, _EmulatorsResultDict]] = {}

    systems_config = safe_load_yaml(defaults_dir / 'configgen-defaults.yml', dict[str, DefaultDict])

    for config_file in configs_dir.iterdir():
        arch = config_file.stem.replace('config_', '')
        config = _load_config(configs_dir / config_file)
        arch_systems_config = safe_load_yaml(
            defaults_dir / f'configgen-defaults-{arch}.yml', dict[str, DefaultDict] | None
        )
        # case when there is no arch file
        if arch_systems_config is None:
            arch_systems_config = {}
        result_systems: dict[str, _EmulatorsResultDict] = {}
        boards = _find_boards_from_config(config)
        for system, system_rules in rules.items():
            # default emulator
            default_emulator = None
            if (arch_emulator := get_deep_value(arch_systems_config, system, 'emulator')) is not MISSING:
                default_emulator = arch_emulator
            elif (system_emulator := get_deep_value(systems_config, system, 'emulator')) is not MISSING:
                default_emulator = system_emulator

            # default core
            default_core = None
            if (arch_core := get_deep_value(arch_systems_config, system, 'core')) is not MISSING:
                default_core = arch_core
            elif (system_core := get_deep_value(systems_config, system, 'core')) is not MISSING:
                default_core = system_core

            emulators = _list_emulators(
                arch, system, system_rules, explanations, config, default_emulator, default_core
            )
            if any(emulators['emulators']):
                emulators['red_flag'] = _has_red_flag(
                    emulators['nb_variants'], emulators['nb_explanations'], emulators['nb_all_explanations']
                )
                result_systems[system] = emulators
        for board in boards:
            result_archs[board] = result_systems

    print(json.dumps(result_archs, indent=2, sort_keys=True, cls=_SortedListEncoder))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('yml', help='es_systems.yml definition file', type=Path)
    parser.add_argument('explanationsYaml', help='explanations.yml definition file', type=Path)
    parser.add_argument('defaultsDir', help='directory containing defaults cores configs', type=Path)
    parser.add_argument('configsDir', help='directory containing config buildroot files', type=Path)
    args = parser.parse_args()
    _generate_report(args.yml, args.explanationsYaml, args.configsDir, args.defaultsDir)
