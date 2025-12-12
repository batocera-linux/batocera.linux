from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, NotRequired
from typing_extensions import TypedDict, TypeForm

import yaml

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping
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


MISSING: Final = object()


def get_deep_value(mapping: Mapping[str, Any], first_key: str, /, *keys: str) -> Any:
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


def is_arch_valid(arch: str, obj: Mapping[str, Any], /) -> bool:
    if 'archs_exclude' in obj and arch in obj['archs_exclude']:
        return False
    return 'archs_include' not in obj or arch in obj['archs_include']


def is_valid_requirements(config: Mapping[str, str | int], requirements: Collection[str], /) -> bool:
    if not requirements:
        return True

    return any(requirement in config for requirement in requirements)


def safe_load_yaml[T](file: Path, type: TypeForm[T], /) -> T:
    return yaml.safe_load(file.read_text())
