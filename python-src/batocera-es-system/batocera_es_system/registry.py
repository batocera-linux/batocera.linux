from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, NotRequired, Protocol, Self, TypedDict, Unpack, cast
from typing_extensions import ReadOnly

from batocera_es_system.shared import ConfiggenDefaults, safe_dump_yaml12, safe_load_yaml12

if TYPE_CHECKING:
    from _typeshed import StrPath


class KeysActionBase(TypedDict):
    trigger: str | list[str]
    mode: NotRequired[Literal['all', 'sequence', 'any']]
    hold: NotRequired[float]
    description: NotRequired[str]


class KeysAction(KeysActionBase):
    type: Literal['exec', 'key']
    target: str | list[str]


class KeysMouseAction(KeysActionBase):
    type: Literal['mouse']


type KeysActions = list[KeysAction | KeysMouseAction]
type KeysConfigDict = dict[str, KeysActions]


class _BaseCustomFeatureDict(TypedDict):
    prompt: str
    description: NotRequired[str]
    group: NotRequired[str]
    submenu: NotRequired[str]
    order: NotRequired[int]
    # only for extensions
    before: NotRequired[str]


class CustomFeaturePresetDict(_BaseCustomFeatureDict):
    preset: str
    preset_parameters: NotRequired[str]


class CustomFeatureChoicesDict(_BaseCustomFeatureDict):
    choices: dict[str, str | float | bool | None]


type CustomFeatureDict = CustomFeaturePresetDict | CustomFeatureChoicesDict


class InfoDict(TypedDict):
    features: NotRequired[list[str]]
    shared_features: NotRequired[list[str]]
    custom_features: NotRequired[dict[str, CustomFeatureDict]]
    keys: NotRequired[KeysConfigDict]


class SystemInfoDict(InfoDict):
    name: str
    disabled: NotRequired[bool]
    exclude_extensions: NotRequired[list[str]]


class CoreInfoDict(InfoDict):
    systems: NotRequired[list[str | SystemInfoDict]]


class EmulatorSystemInfoDict(SystemInfoDict):
    as_emulator: NotRequired[str]
    as_core: NotRequired[str | list[str]]


class EmulatorInfoDict(InfoDict):
    cores: NotRequired[dict[str, CoreInfoDict]]
    systems: NotRequired[list[str | EmulatorSystemInfoDict]]


class CommentDict(TypedDict):
    emulator: str
    core: NotRequired[str]


@dataclass(slots=True)
class _FeatureBase:
    prompt: str
    description: str | None
    group: str | None
    submenu: str | None
    order: int | None

    def _get_translatable_strings(self) -> Iterator[str]:
        if self.description is not None:
            yield self.description

        if self.submenu is not None:
            yield self.submenu

        if self.group is not None:
            yield self.group

        yield self.prompt

    def _to_dict(self) -> dict[str, object]:
        data: dict[str, object] = {
            'prompt': self.prompt,
        }

        if self.description or self.description is None:
            data['description'] = self.description
        if self.group is not None:
            data['group'] = self.group
        if self.submenu is not None:
            data['submenu'] = self.submenu
        if self.order is not None:
            data['order'] = self.order

        return data


@dataclass(slots=True)
class PresetFeature(_FeatureBase):
    preset: str
    preset_parameters: str | None

    def _to_dict(self) -> dict[str, object]:
        data = super(PresetFeature, self)._to_dict()

        data['preset'] = self.preset

        if self.preset_parameters is not None:
            data['preset_parameters'] = self.preset_parameters

        return data

    @classmethod
    def from_dict(cls, data: CustomFeaturePresetDict, /) -> Self:
        return cls(
            prompt=data['prompt'],
            description=data.get('description', ''),
            group=data.get('group'),
            submenu=data.get('submenu'),
            order=data.get('order'),
            preset=data['preset'],
            preset_parameters=data.get('preset_parameters'),
        )


@dataclass(slots=True)
class ChoiceFeature(_FeatureBase):
    choices: dict[str, str | float | bool | None]

    def _get_translatable_strings(self) -> Iterator[str]:
        yield from super(ChoiceFeature, self)._get_translatable_strings()
        yield from self.choices

    def _to_dict(self) -> dict[str, object]:
        data = super(ChoiceFeature, self)._to_dict()

        data['choices'] = self.choices

        return data

    @classmethod
    def from_dict(cls, data: CustomFeatureChoicesDict, /) -> Self:
        return cls(
            prompt=data['prompt'],
            description=data.get('description', ''),
            group=data.get('group'),
            submenu=data.get('submenu'),
            order=data.get('order'),
            choices=dict(data['choices']),
        )


type CustomFeature = PresetFeature | ChoiceFeature


def _dict_to_custom_features_iter(
    data: Mapping[str, CustomFeatureDict] | Iterable[tuple[str, CustomFeatureDict]], /
) -> Iterator[tuple[str, CustomFeature]]:
    items = cast('Iterable[tuple[str, CustomFeatureDict]]', data.items() if isinstance(data, Mapping) else data)

    yield from (
        (key, PresetFeature.from_dict(value) if 'preset' in value else ChoiceFeature.from_dict(value))
        for key, value in items
    )


def _dict_to_custom_features(
    data: Mapping[str, CustomFeatureDict] | Iterable[tuple[str, CustomFeatureDict]] | None, /
) -> dict[str, CustomFeature] | None:
    if data is None:
        return None

    return dict(_dict_to_custom_features_iter(data))


def _extend_custom_features(
    base: dict[str, CustomFeature] | None,
    extend: Mapping[str, CustomFeatureDict] | None,
    /,
) -> dict[str, CustomFeature] | None:
    if extend is None:
        return base

    if base is None:
        return _dict_to_custom_features(extend)

    before: dict[str, list[tuple[str, CustomFeatureDict]]] = defaultdict(list)
    append: list[tuple[str, CustomFeatureDict]] = []

    for key, value in extend.items():
        if 'before' in value:
            before[value['before']].append((key, value))
        else:
            append.append((key, value))

    new_custom_features: dict[str, CustomFeature] = {}
    for key, value in base.items():
        if key in before:
            new_custom_features.update(_dict_to_custom_features_iter(before[key]))

        new_custom_features[key] = value

    new_custom_features.update(_dict_to_custom_features_iter(append))
    return new_custom_features


class HasFeatures(Protocol):
    features: list[str] | None


@dataclass(slots=True)
class _BaseInfo[I: InfoDict]:
    features: list[str] | None
    shared_features: list[str] | None
    custom_features: dict[str, CustomFeature] | None
    keys: KeysConfigDict | None

    def _get_translatable_strings(self) -> Iterator[str]:
        if self.custom_features:
            yield from chain.from_iterable(
                feature._get_translatable_strings() for feature in self.custom_features.values()
            )

    def extend(self, extension: I, /) -> None:
        if 'features' in extension:
            self.features = (self.features or []) + extension['features']
        if 'shared_features' in extension:
            self.shared_features = (self.shared_features or []) + extension['shared_features']
        if 'custom_features' in extension:
            self.custom_features = _extend_custom_features(self.custom_features, extension['custom_features'])
        if 'keys' in extension:
            self.keys = extension['keys']

    def _to_dict(self) -> dict[str, object]:
        data: dict[str, object] = {}

        if self.features is not None:
            data['features'] = self.features
        if self.shared_features is not None:
            data['shared_features'] = self.shared_features
        if self.custom_features is not None:
            data['custom_features'] = {key: value._to_dict() for key, value in self.custom_features.items()}
        if self.keys is not None:
            data['keys'] = self.keys

        return data


@dataclass(slots=True)
class SystemInfo(_BaseInfo[SystemInfoDict | EmulatorSystemInfoDict]):
    name: str
    disabled: bool | None
    as_emulator: str | None
    as_core: list[str] | None
    exclude_extensions: list[str] | None

    def extend(self, extension: SystemInfoDict | EmulatorSystemInfoDict, /) -> None:
        super(SystemInfo, self).extend(extension)

        self.disabled = extension.get('disabled')

        if 'as_emulator' in extension:
            self.as_emulator = extension['as_emulator']
        if 'as_core' in extension:
            as_core = extension['as_core']
            self.as_core = (self.as_core or []).extend([as_core] if isinstance(as_core, str) else as_core)
        if 'exclude_extensions' in extension:
            self.exclude_extensions = (self.exclude_extensions or []) + extension['exclude_extensions']

    def _to_dict(self) -> dict[str, object]:
        data = super(SystemInfo, self)._to_dict()

        if self.as_emulator is not None:
            data['as_emulator'] = self.as_emulator
        if self.as_core:
            data['as_core'] = self.as_core[0] if len(self.as_core) == 1 else self.as_core
        if self.exclude_extensions is not None:
            data['exclude_extensions'] = self.exclude_extensions

        return {'name': self.name, **data}

    @classmethod
    def from_data(cls, data: str | SystemInfoDict | EmulatorSystemInfoDict, /) -> Self:
        if isinstance(data, str):
            return cls(
                name=data,
                features=None,
                shared_features=None,
                custom_features=None,
                disabled=None,
                as_emulator=None,
                as_core=None,
                exclude_extensions=None,
                keys=None,
            )

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: SystemInfoDict | EmulatorSystemInfoDict, /) -> Self:
        as_core = data.get('as_core')
        return cls(
            name=data['name'],
            features=data.get('features'),
            shared_features=data.get('shared_features'),
            custom_features=_dict_to_custom_features(data.get('custom_features')),
            disabled=data.get('disabled'),
            as_emulator=data.get('as_emulator'),
            as_core=[as_core] if isinstance(as_core, str) else as_core,
            exclude_extensions=data.get('exclude_extensions'),
            keys=data.get('keys'),
        )


def _system_info_list_to_dict(
    systems: Iterable[str | SystemInfoDict | EmulatorSystemInfoDict], /
) -> dict[str, SystemInfo]:
    systems_dict: dict[str, SystemInfo] = {}
    duplicates: set[str] = set()

    for system in systems:
        system_info = SystemInfo.from_data(system)

        if system_info.name in systems_dict:
            duplicates.add(system_info.name)

        systems_dict[system_info.name] = system_info

    if duplicates:
        raise ValueError(f'Duplicate system definitions: {", ".join(sorted(duplicates))}')

    return systems_dict


@dataclass(slots=True)
class _FileInfoBase[I: CoreInfoDict | EmulatorInfoDict](_BaseInfo[I]):
    name: str
    systems: dict[str, SystemInfo]

    @property
    def filename(self) -> str:
        raise NotImplementedError

    def write(self, dest: Path, /) -> None:
        safe_dump_yaml12(self._to_dict(), dest / self.filename)

    def _to_dict(self) -> dict[str, object]:
        data = super(_FileInfoBase, self)._to_dict()

        if self.systems:
            data['systems'] = [system._to_dict() for system in self.systems.values()]

        return data

    def _get_comment_dict(self) -> CommentDict:
        raise NotImplementedError

    def _get_translatable_strings(self) -> Iterator[str]:
        yield from super(_FileInfoBase, self)._get_translatable_strings()
        yield from chain.from_iterable(system._get_translatable_strings() for system in self.systems.values())

    def get_translation_data(self) -> Iterator[tuple[str, CommentDict]]:
        comment = self._get_comment_dict()
        yield from ((string, comment) for string in self._get_translatable_strings())

    def load_extensions(self, extensions: Iterable[Path], /) -> None:
        for extension in extensions:
            self.extend(safe_load_yaml12(extension, I))

    def extend(self, extension: I, /) -> None:
        super(_FileInfoBase, self).extend(extension)

        if 'systems' in extension:
            for system_info in extension['systems']:
                system_name = system_info if isinstance(system_info, str) else system_info['name']
                if system_name in self.systems:
                    if not isinstance(system_info, str):
                        self.systems[system_name].extend(system_info)
                else:
                    self.systems[system_name] = SystemInfo.from_data(system_info)

    @classmethod
    def from_dict(cls, data: I, /, **kwargs: Unpack[FileInfoDict]) -> Self:
        raise NotImplementedError

    @classmethod
    def from_info(cls, info: Path, file_info: FileInfoDict | None = None, /) -> Self:
        if file_info is None:
            file_info = get_file_info(info)

        data = safe_load_yaml12(info, I) or cast('I', {})
        return cls.from_dict(data, **file_info)


@dataclass(slots=True)
class CoreInfo(_FileInfoBase[CoreInfoDict]):
    emulator: str

    @property
    def filename(self) -> str:
        return f'{self.name}.{self.emulator}.core.yml'

    def _get_comment_dict(self) -> CommentDict:
        return {
            'emulator': self.emulator,
            'core': self.name,
        }

    @classmethod
    def from_dict(cls, data: CoreInfoDict, /, *, name: str, emulator: str, **kwargs: object) -> Self:
        return cls(
            name=name,
            emulator=emulator,
            features=data.get('features'),
            shared_features=data.get('shared_features'),
            custom_features=_dict_to_custom_features(data.get('custom_features')),
            systems=_system_info_list_to_dict(data.get('systems', [])),
            keys=data.get('keys'),
        )


@dataclass(slots=True)
class EmulatorInfo(_FileInfoBase[EmulatorInfoDict]):
    cores: dict[str, CoreInfo]

    @property
    def filename(self) -> str:
        return f'{self.name}.emulator.yml'

    def _get_comment_dict(self) -> CommentDict:
        name = self.name
        if name == '_shared' or name == '_global':
            name = name[1:]  # strip leading underscore for shared/global

        return {'emulator': name}

    def get_translation_data(self) -> Iterator[tuple[str, CommentDict]]:
        if self.cores:
            yield from chain.from_iterable(core.get_translation_data() for core in self.cores.values())

        yield from super(EmulatorInfo, self).get_translation_data()

    def add_core(self, core: CoreInfo, /) -> None:
        if core.name in self.cores:
            raise ValueError(f'Core {core.name} is already registered for emulator {self.name}')

        self.cores[core.name] = core

    def extend(self, extension: EmulatorInfoDict, /) -> None:
        super(EmulatorInfo, self).extend(extension)

        if 'cores' in extension:
            for core_name, core_info in extension['cores'].items():
                if core_name in self.cores:
                    self.cores[core_name].extend(core_info)
                else:
                    self.cores[core_name] = CoreInfo.from_dict(
                        core_info,
                        name=core_name,
                        emulator=self.name,
                    )

    def _to_dict(self) -> dict[str, object]:
        data = super(EmulatorInfo, self)._to_dict()

        if self.cores:
            data['cores'] = {core_name: core._to_dict() for core_name, core in self.cores.items()}

        return data

    @classmethod
    def from_dict(cls, data: EmulatorInfoDict, /, *, name: str, **kwargs: object) -> Self:
        return cls(
            name=name,
            features=data.get('features'),
            shared_features=data.get('shared_features'),
            custom_features=_dict_to_custom_features(data.get('custom_features')),
            systems=_system_info_list_to_dict(data.get('systems', [])),
            cores={
                core_name: CoreInfo.from_dict(
                    core_info,
                    name=core_name,
                    emulator=name,
                )
                for core_name, core_info in data.get('cores', {}).items()
            }
            if 'cores' in data
            else {},
            keys=data.get('keys'),
        )


type FileInfoKind = Literal['emulator', 'core']


class FileInfoDict(TypedDict):
    kind: FileInfoKind
    name: str
    emulator: str
    is_extension: bool


def get_file_info(file: Path, /) -> FileInfoDict:
    kind: FileInfoKind
    name: str
    emulator: str
    is_extension = False

    file = Path(file)
    parts = file.stem.rsplit('.', 3)
    parts.reverse()

    match parts:
        case [('emulator' | 'core') as _kind, _emulator, *rest]:
            kind = _kind
            emulator = _emulator

            if _kind == 'emulator':
                name = _emulator

                if rest:
                    is_extension = True
            else:
                name = rest[0]

                if len(rest) > 1:
                    is_extension = True
        case _:
            raise ValueError(f'File ({file.name}) must be an emulator or core YAML file')

    return cast(
        'FileInfoDict',
        {
            'kind': kind,
            'name': name,
            'emulator': emulator,
            'is_extension': is_extension,
        },
    )


@dataclass(slots=True)
class RegistryInfo[T: EmulatorInfo | CoreInfo]:
    name: str
    emulator: str
    filename: str
    info: T

    def extend(self, extension: Path, /) -> None:
        self.info.extend(safe_load_yaml12(extension, Any))

    def register(self, dest: Path, /) -> None:
        info_dict = self.info._to_dict()

        dest.mkdir(parents=True, exist_ok=True)
        safe_dump_yaml12(info_dict, dest / self.filename)

    @classmethod
    def from_info(cls, info_path: Path, file_info: FileInfoDict | None = None, /) -> RegistryInfo[Any]:
        if file_info is None:
            file_info = get_file_info(info_path)

        if file_info['is_extension']:
            raise ValueError(f'File ({info_path.name}) must be passed as an extension')

        return cls(
            name=file_info['name'],
            emulator=file_info['emulator'],
            filename=info_path.name,
            info=cast('T', CoreInfo if file_info['kind'] == 'core' else EmulatorInfo).from_info(info_path, file_info),
        )


class CoreMetadata(TypedDict):
    default: ReadOnly[bool]
    incompatible_extensions: ReadOnly[list[str]]


type EmulatorCoresMetadataDict = dict[str, CoreMetadata]
type EmulatorCoresMetadataMapping = Mapping[str, CoreMetadata]


type EmulatorsMetadataDict = dict[str, EmulatorCoresMetadataDict]
type EmulatorsMetadataMapping = Mapping[str, EmulatorCoresMetadataMapping]


type SystemsMetadataDict = dict[str, EmulatorsMetadataDict]
type SystemsMetadataMapping = Mapping[str, EmulatorsMetadataMapping]

type EmulatorsBySystemDict = dict[str, dict[str, dict[str, EmulatorInfo]]]
type EmulatorsBySystemMapping = Mapping[str, Mapping[str, Mapping[str, EmulatorInfo]]]


@dataclass(slots=True)
class Registry:
    _emulators: dict[str, EmulatorInfo]
    _cores: dict[str, dict[str, CoreInfo]]
    _emulator_defs: dict[str, EmulatorInfo] | None = field(init=False, default=None)

    @property
    def shared_defs(self) -> EmulatorInfo:
        shared_defs = self._emulators.get('_shared')

        if shared_defs is None:
            raise ValueError('Missing shared emulator definitions')

        return shared_defs

    @property
    def global_defs(self) -> EmulatorInfo:
        global_defs = self._emulators.get('_global')

        if global_defs is None:
            raise ValueError('Missing global emulator definitions')

        return global_defs

    @property
    def emulator_defs(self) -> Mapping[str, EmulatorInfo]:
        if self._emulator_defs is None:
            for emulator_cores in self._cores.values():
                for core in emulator_cores.values():
                    if core.emulator not in self._emulators:
                        raise ValueError(f'Core {core.name}.{core.emulator} references unregistered emulator')

                    self._emulators[core.emulator].add_core(core)

            self._emulator_defs = {
                key: value for key, value in self._emulators.items() if key not in ('_shared', '_global')
            }

        return self._emulator_defs

    def _iter_system_emulator_cores(self) -> Iterator[tuple[SystemInfo, str, EmulatorInfo, str]]:
        for emulator in self.emulator_defs.values():
            if not emulator.cores and emulator.systems:
                for system in emulator.systems.values():
                    if system.disabled:
                        continue

                    emulator_name = system.as_emulator or emulator.name
                    core_names = system.as_core or [emulator_name]

                    for core_name in core_names:
                        yield system, emulator_name, emulator, core_name
            elif emulator.cores and not emulator.systems:
                for core in emulator.cores.values():
                    for system in core.systems.values():
                        if system.disabled:
                            continue

                        yield system, emulator.name, emulator, core.name
            elif emulator.cores and emulator.systems:
                for system in emulator.systems.values():
                    if system.disabled:
                        continue

                    for core in emulator.cores.values():
                        yield system, emulator.name, emulator, core.name

    @property
    def emulators_by_system(self) -> EmulatorsBySystemMapping:
        emulators_by_system: EmulatorsBySystemDict = defaultdict(lambda: defaultdict(dict))

        for system, emulator_name, emulator, core_name in self._iter_system_emulator_cores():
            emulators_by_system[system.name][emulator_name][core_name] = emulator

        return emulators_by_system

    def get_systems_metadata(self, configgen_defaults: ConfiggenDefaults, /) -> SystemsMetadataMapping:
        system_core_data: SystemsMetadataDict = defaultdict(lambda: defaultdict(dict))

        for system, emulator_name, _, core_name in self._iter_system_emulator_cores():
            system_core_data[system.name][emulator_name][core_name] = {
                'incompatible_extensions': system.exclude_extensions or [],
                'default': emulator_name == configgen_defaults.get(system.name, 'emulator')
                and core_name == configgen_defaults.get(system.name, 'core'),
            }

        return system_core_data

    def __iter__(self) -> Iterator[EmulatorInfo]:
        return chain([self.shared_defs, self.global_defs], self.emulator_defs.values())

    @classmethod
    def load_files(cls, files: Iterable[StrPath], /) -> Self:
        emulators: dict[str, EmulatorInfo] = {}
        cores: dict[str, dict[str, CoreInfo]] = defaultdict(dict)
        extensions: dict[str, list[Path]] = defaultdict(list)
        core_extensions: dict[str, dict[str, list[Path]]] = defaultdict(lambda: defaultdict(list))

        for file in files:
            file = Path(file)
            file_info = get_file_info(file)

            if not file_info['is_extension']:
                if file_info['kind'] == 'emulator':
                    emulators[file_info['name']] = EmulatorInfo.from_info(file, file_info)
                else:
                    cores[file_info['emulator']][file_info['name']] = CoreInfo.from_info(file, file_info)
            else:
                (
                    extensions[file_info['name']]
                    if file_info['kind'] == 'emulator'
                    else core_extensions[file_info['emulator']][file_info['name']]
                ).append(file)

        for emulator_name, emulator in emulators.items():
            for extension in extensions.get(emulator_name, []):
                emulator.extend(safe_load_yaml12(extension, EmulatorInfoDict))

        for emulator_name, emulator_cores in cores.items():
            for core_name, core in emulator_cores.items():
                for extension in core_extensions.get(emulator_name, {}).get(core_name, []):
                    core.extend(safe_load_yaml12(extension, CoreInfoDict))

        return cls(_emulators=emulators, _cores=cores)

    @classmethod
    def load_path_file(cls, path_file: StrPath, /) -> Self:
        path_file = Path(path_file)
        return cls.load_files(path_file.read_text().strip().split())

    @staticmethod
    def register_files(dest: Path, files: list[Path], /) -> None:
        registry = Registry.load_files(files)

        dest.mkdir(parents=True, exist_ok=True)

        for emulator in registry._emulators.values():
            emulator.write(dest)

        for emulator_cores in registry._cores.values():
            for core in emulator_cores.values():
                core.write(dest)
