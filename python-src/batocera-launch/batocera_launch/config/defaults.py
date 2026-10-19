# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import yaml

from batocera_common.dict import merge

from ..paths import LAUNCH_DEFAULTS_DIR

if TYPE_CHECKING:
    from pathlib import Path


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
        merge(config, arch_defaults['default'])

    if system_name in defaults:
        merge(config, defaults[system_name])

    if system_name in arch_defaults:
        merge(config, arch_defaults[system_name])

    return config


def load_system_defaults(system_name: str, /) -> dict[str, Any]:
    defaults = load_defaults(system_name, LAUNCH_DEFAULTS_DIR / 'config.yml', LAUNCH_DEFAULTS_DIR / 'config-arch.yml')

    # In the yaml files, the "options" structure is not flat, so we have to flatten it here
    # because the options are flat in batocera.conf to make it easier for end users to edit
    data: dict[str, Any] = {'emulator': defaults['emulator'], 'core': defaults['core']}

    if 'options' in defaults:
        merge(data, defaults['options'])

    return data
