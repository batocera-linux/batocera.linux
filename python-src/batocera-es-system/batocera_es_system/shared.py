from __future__ import annotations

from collections import deque
from dataclasses import InitVar, dataclass, field
from typing import TYPE_CHECKING, Any, Final, NotRequired, Self, overload
from typing_extensions import Sentinel, TypedDict, TypeForm

import ruamel.yaml
import yaml

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Mapping
    from pathlib import Path


class DefaultDict(TypedDict):
    emulator: NotRequired[str]
    core: NotRequired[str]
    options: NotRequired[dict[str, str | int | bool]]


# es_systems.yml definitions


class CoreDict(TypedDict):
    requireAnyOf: list[str]
    incompatible_extensions: NotRequired[list[str]]


class EmulatorDict(TypedDict, extra_items=CoreDict):
    archs_include: NotRequired[list[str]]
    archs_exclude: NotRequired[list[str]]


class SystemDict(TypedDict, extra_items=str):
    name: str
    manufacturer: str
    release: int
    hardware: str
    path: NotRequired[str | None]
    extensions: list[str]
    emulators: NotRequired[dict[str, EmulatorDict]]
    platform: NotRequired[str | None]
    group: NotRequired[str | None]
    theme: NotRequired[str]


type SystemsData = dict[str, SystemDict]
type SystemsDataMapping = Mapping[str, SystemDict]


# es_systems.yml plus configgen defaults


class DefaultsDict(TypedDict):
    emulator: str | None
    core: str | None


MISSING: Final = Sentinel('MISSING')


def get_deep_value(mapping: Mapping[str, Any], first_key: str, /, *keys: str) -> Any | MISSING:
    """
    Get a deep value from a nested mapping. Returns MISSING if any key is not found.
    """
    result = mapping

    for key in [first_key, *keys]:
        try:
            result = result[key]
        except KeyError:
            return MISSING

    return result


def safe_load_yaml12[T](file: Path, type: TypeForm[T], /) -> T:
    yml = ruamel.yaml.YAML(typ='safe', pure=True)
    with file.open() as f:
        return yml.load(f)  # pyright: ignore


def safe_dump_yaml12(data: object, file: Path, /) -> None:
    yaml = ruamel.yaml.YAML(typ='safe', pure=True)
    yaml.default_flow_style = False
    yaml.sort_base_mapping_type_on_output = False  # pyright: ignore
    yaml.indent(mapping=2, sequence=4, offset=2)  # pyright: ignore
    yaml.dump(data, file)  # pyright: ignore


def safe_load_yaml[T](file: Path, type: TypeForm[T], /) -> T:
    return yaml.safe_load(file.read_text())


def write_xml(file: Path, root: str, lines: Iterable[str], /) -> None:
    with file.open('w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
        f.write(f'<{root}>\n')
        f.writelines(f'{line}\n' for line in lines)
        f.write(f'</{root}>\n')


def protect_xml(strval: object, /) -> str:
    strval = str(strval)
    strval = strval.replace('&', '&amp;')
    strval = strval.replace('<', '&lt;')
    strval = strval.replace('>', '&gt;')
    strval = strval.replace('"', '&quot;')
    return strval.replace('\n', '&#x0a;')


def to_xml_attribute(name: str, string: str | int | None, /) -> str:
    return f' {name}="{protect_xml(string)}"' if string else ''


_NOTHING: Final = Sentinel('_NOTHING')


@dataclass(slots=True)
class peekable[T]:
    iterable: InitVar[Iterable[T]]

    _cache: deque[T] = field(init=False)
    _iter: Iterator[T] = field(init=False)

    def __post_init__(self, iterable: Iterable[T]) -> None:
        self._iter = iter(iterable)
        self._cache = deque()

    def __bool__(self) -> bool:
        try:
            self.peek()
        except StopIteration:
            return False

        return True

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> T:
        if self._cache:
            return self._cache.popleft()

        return next(self._iter)

    @overload
    def peek(self) -> T: ...

    @overload
    def peek[U](self, default: U) -> T | U: ...

    def peek[U](self, default: U = _NOTHING) -> T | U:
        if not self._cache:
            try:
                self._cache.append(next(self._iter))
            except StopIteration:
                if default is _NOTHING:
                    raise

                return default

        return self._cache[0]


def wrap_tag(
    tag: str, iterable: Iterable[str], /, *, attributes: str = '', indent: str = '', self_closing: bool = False
) -> Iterator[str]:
    if attributes:
        attributes = f' {attributes}'

    tag_start = f'{indent}<{tag}{attributes}'

    iterator = peekable(iterable)

    if not iterator:
        if self_closing:
            yield f'{tag_start} />'

        return

    yield f'{tag_start}>'
    yield from iterator
    yield f'{indent}</{tag}>'


@dataclass(slots=True)
class ConfiggenDefaults:
    defaults: dict[str, DefaultDict]
    arch_defaults: dict[str, DefaultDict]

    def get(self, system_name: str, key: str) -> str | None:
        if (arch_value := get_deep_value(self.arch_defaults, system_name, key)) is not MISSING:
            return arch_value
        if (value := get_deep_value(self.defaults, system_name, key)) is not MISSING:
            return value
        return None

    @classmethod
    def for_defaults(cls, defaults: Path, arch_defaults: Path, /) -> Self:
        return cls(
            safe_load_yaml(defaults, dict[str, DefaultDict]),
            safe_load_yaml(arch_defaults, dict[str, DefaultDict] | None) or {},
        )

    @classmethod
    def for_directory(cls, directory: Path, /) -> Self:
        return cls.for_defaults(directory / 'configgen-defaults.yml', directory / 'configgen-defaults-arch.yml')
