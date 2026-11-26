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

"""es_savestates.cfg for ES and savestates.json for batocera-launch, from the emulators' `savestates`."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Final

from batocera_es_system.shared import protect_xml, write_xml

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping
    from pathlib import Path

    from batocera_es_system.registry import Registry

# es_savestates.cfg's attributes, in its order; the rest of a spec is for batocera-launch
ES_ATTRIBUTES: Final = (
    'directory',
    'file',
    'image',
    'nofileextension',
    'firstslot',
    'autosave',
    'autosave_file',
    'autosave_image',
    'incremental',
)


def _value(value: object, /) -> str:
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return protect_xml(value)


def emulator_line(name: str, spec: Mapping[str, Any], /) -> str:
    name_attribute = f'name="{protect_xml(name)}"'
    attributes = ' '.join(f'{key}="{_value(spec[key])}"' for key in ES_ATTRIBUTES if key in spec)
    # names padded as the hand-written file had them
    return f'  <emulator {name_attribute:<18} {attributes} />'


def specs(registry: Registry, /) -> dict[str, Mapping[str, Any]]:
    return {
        name: emulator.savestates
        for name, emulator in sorted(registry.emulator_defs.items())
        if emulator.savestates is not None
    }


def _lines(registry: Registry, /) -> Iterator[str]:
    for name, spec in specs(registry).items():
        if 'directory' not in spec:
            raise ValueError(f'{name}: savestates needs a directory')
        yield emulator_line(name, spec)


def build(registry: Registry, build_dir: Path, /) -> None:
    es_savestates_path = build_dir / 'es_savestates.cfg'
    print(f'Generating {es_savestates_path}...')
    write_xml(es_savestates_path, 'savestates', _lines(registry))

    (build_dir / 'savestates.json').write_text(json.dumps(specs(registry), indent=2, sort_keys=True) + '\n')
