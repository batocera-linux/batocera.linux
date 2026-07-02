from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

import yaml

from batocera_launch.paths import DEFAULTS_DIR

if TYPE_CHECKING:
    from pathlib import Path


# adapted from https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
def _dict_merge(destination: dict[str, Any], source: Mapping[str, Any]) -> None:
    """Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param destination: dict onto which the merge is executed
    :param source: dict merged into destination
    :return: None
    """
    for key, value in source.items():
        if key in destination and isinstance(destination[key], dict) and isinstance(value, Mapping):
            _dict_merge(destination[key], value)  # pyright: ignore[reportUnknownArgumentType]
        else:
            destination[key] = value


def load_defaults(system_name: str, default_yml: Path, default_arch_yml: Path, /) -> dict[str, Any]:
    defaults = yaml.load(default_yml.read_text(), Loader=yaml.CLoader)

    arch_defaults: dict[str, Any] = {}
    if default_arch_yml.exists():
        loaded_arch_defaults = yaml.load(default_arch_yml.read_text(), Loader=yaml.CLoader)
        if loaded_arch_defaults is not None:
            arch_defaults = loaded_arch_defaults

    config: dict[str, Any] = {}

    if 'default' in defaults:
        config = defaults['default']

    if 'default' in arch_defaults:
        _dict_merge(config, arch_defaults['default'])

    if system_name in defaults:
        _dict_merge(config, defaults[system_name])

    if system_name in arch_defaults:
        _dict_merge(config, arch_defaults[system_name])

    return config


def load_system_defaults(system_name: str, /) -> dict[str, Any]:
    defaults = load_defaults(
        system_name, DEFAULTS_DIR / 'configgen-defaults.yml', DEFAULTS_DIR / 'configgen-defaults-arch.yml'
    )

    # In the yaml files, the "options" structure is not flat, so we have to flatten it here
    # because the options are flat in batocera.conf to make it easier for end users to edit
    data: dict[str, Any] = {'emulator': defaults['emulator'], 'core': defaults['core']}

    if 'options' in defaults:
        _dict_merge(data, defaults['options'])

    return data
