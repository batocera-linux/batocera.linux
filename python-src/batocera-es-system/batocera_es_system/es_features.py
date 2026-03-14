from __future__ import annotations

from itertools import chain
from typing import TYPE_CHECKING

from batocera_es_system.registry import (
    ChoiceFeature,
    CoreInfo,
    CustomFeature,
    EmulatorInfo,
    HasFeatures,
    PresetFeature,
    Registry,
    SystemInfo,
)
from batocera_es_system.shared import (
    protect_xml,
    to_xml_attribute,
    wrap_tag,
    write_xml,
)

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping
    from pathlib import Path


def _features_to_attribute(obj: HasFeatures, /) -> str:
    return protect_xml('' if obj.features is None else ', '.join(obj.features))


def _shared_features_to_xml(shared_features: list[str] | None, indent: str, /) -> Iterator[str]:
    if not shared_features:
        return

    for shared in shared_features:
        yield f'{indent}<sharedFeature value="{protect_xml(shared)}" />'


def _custom_features_to_xml(features: Mapping[str, CustomFeature] | None, indent: str, /) -> Iterator[str]:
    if not features:
        return

    for name, feature in features.items():
        submenu = to_xml_attribute('submenu', feature.submenu)
        group = to_xml_attribute('group', feature.group)
        order = to_xml_attribute('order', feature.order)
        description = protect_xml(feature.description)
        preset = ''

        if isinstance(feature, PresetFeature):
            if feature.preset:
                preset = to_xml_attribute('preset', feature.preset)
            if feature.preset_parameters:
                preset += to_xml_attribute('preset-parameters', feature.preset_parameters)

        yield f'{indent}<feature name="{protect_xml(feature.prompt)}"{submenu}{group}{order} value="{
            protect_xml(name)
        }" description="{description}"{preset}>'

        if isinstance(feature, ChoiceFeature):
            for choice_name, choice in feature.choices.items():
                yield f'{indent}  <choice name="{protect_xml(choice_name)}" value="{protect_xml(choice)}" />'

        yield f'{indent}</feature>'


def _system_to_xml(system: SystemInfo, /, *, indent: str = '') -> Iterator[str]:
    if not system.shared_features and not system.custom_features:
        return

    yield f'{indent}<system name="{protect_xml(system.name)}" features="{_features_to_attribute(system)}" >'
    yield from _shared_features_to_xml(system.shared_features, f'{indent}  ')
    yield from _custom_features_to_xml(system.custom_features, f'{indent}  ')
    yield f'{indent}</system>'


def _systems_to_xml(systems: Mapping[str, SystemInfo], /, *, indent: str = '') -> Iterator[str]:
    if not systems:
        return

    yield from wrap_tag(
        'systems',
        chain.from_iterable(_system_to_xml(system, indent=f'{indent}  ') for system in systems.values()),
        indent=indent,
    )


def _core_to_xml(core: CoreInfo, /, *, indent: str = '') -> Iterator[str]:
    if not core.shared_features and not core.custom_features and not core.systems:
        return

    yield from wrap_tag(
        'core',
        chain(
            _shared_features_to_xml(core.shared_features, f'{indent}  '),
            _custom_features_to_xml(core.custom_features, f'{indent}  '),
            _systems_to_xml(core.systems, indent=f'{indent}  '),
        ),
        indent=indent,
        attributes=f'name="{protect_xml(core.name)}" features="{_features_to_attribute(core)}"',
        self_closing=core.features is not None,
    )


def _cores_to_xml(cores: dict[str, CoreInfo], /, *, indent: str = '') -> Iterator[str]:
    return wrap_tag(
        'cores', chain.from_iterable(_core_to_xml(core, indent=f'{indent}  ') for core in cores.values()), indent=indent
    )


def _emulator_to_xml(emulator: EmulatorInfo, /, *, indent: str = '') -> Iterator[str]:
    if (
        emulator.features is None
        and not emulator.cores
        and not emulator.systems
        and not emulator.custom_features
        and not emulator.shared_features
    ):
        return

    attributes = ''

    if emulator.name == '_shared':
        tag_name = 'sharedFeatures'
    elif emulator.name == '_global':
        tag_name = 'globalFeatures'
    else:
        tag_name = 'emulator'
        attributes = f'name="{protect_xml(emulator.name)}" features="{_features_to_attribute(emulator)}"'

    yield from wrap_tag(
        tag_name,
        chain(
            _cores_to_xml(emulator.cores, indent=f'{indent}  '),
            _systems_to_xml(emulator.systems, indent=f'{indent}  '),
            _shared_features_to_xml(emulator.shared_features, f'{indent}  '),
            _custom_features_to_xml(emulator.custom_features, f'{indent}  '),
        ),
        attributes=attributes,
        indent=indent,
        self_closing=emulator.features is not None,
    )


def build(registry: Registry, build_dir: Path, /) -> None:
    es_features_path = build_dir / 'es_features.cfg'

    print(f'Generating {es_features_path}...')

    write_xml(
        es_features_path,
        'features',
        chain(
            _emulator_to_xml(registry.shared_defs, indent='  '),
            _emulator_to_xml(registry.global_defs, indent='  '),
            chain.from_iterable(
                _emulator_to_xml(emulator, indent='  ') for emulator in registry.emulator_defs.values()
            ),
        ),
    )
