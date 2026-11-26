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

import json
from pathlib import Path
from typing import Final

import pytest

from batocera_es_system.es_savestates import build
from batocera_es_system.registry import Registry

_PACKAGES: Final = Path(__file__).resolve().parents[3] / 'package' / 'batocera'

# the hand-written es_savestates.cfg these emulators had before it was generated
_HAND_WRITTEN: Final = {
    'libretro': '  <emulator name="libretro"    directory="{{system}}" file="{{romfilename}}.state{{slot}}" image="{{romfilename}}.state{{slot}}.png" nofileextension="true" firstslot="0" autosave="true" autosave_file="{{romfilename}}.state.auto" autosave_image="{{romfilename}}.state.auto.png" incremental="true" />',
    'dolphin': '  <emulator name="dolphin"     directory="dolphin-emu/StateSaves" file="{{romfilename}}.s{{slot2d}}" image="{{romfilename}}.s{{slot2d}}.png" nofileextension="false" firstslot="1" autosave="false" incremental="true" />',
    'mupen64plus': '  <emulator name="mupen64plus" directory="n64" file="{{romfilename}}.st{{slot0}}" image="{{romfilename}}.st{{slot0}}.png" nofileextension="false" firstslot="0" autosave="false" incremental="true" />',
    'ppsspp': '  <emulator name="ppsspp"      directory="psp" file="{{romfilename}}_{{slot0}}.ppst" image="{{romfilename}}_{{slot0}}.jpg" nofileextension="true" firstslot="0" autosave="false" />',
    'pcsx2': '  <emulator name="pcsx2"       directory="ps2/pcsx2/sstates" file="{{romfilename}}.{{slot0}}.p2s" image="{{romfilename}}.{{slot0}}.jpg" nofileextension="false" firstslot="1" autosave="true" autosave_file="{{romfilename}}.p2s.auto" autosave_image="{{romfilename}}.p2s.auto.jpg" incremental="true" />',
}


@pytest.fixture(scope='module')
def generated(tmp_path_factory: pytest.TempPathFactory) -> Path:
    files = [path for path in _PACKAGES.rglob('*.emulator.yml') if path.name.count('.') == 2]
    output = tmp_path_factory.mktemp('es')
    build(Registry.load_files(files), output)
    return output


def test_existing_lines_are_unchanged(generated: Path) -> None:
    lines = {
        line.split('"')[1]: line
        for line in (generated / 'es_savestates.cfg').read_text().splitlines()
        if line.startswith('  <emulator ')
    }

    for name, line in _HAND_WRITTEN.items():
        assert lines[name] == line


def test_the_file_is_a_savestates_document(generated: Path) -> None:
    text = (generated / 'es_savestates.cfg').read_text()

    assert text.startswith('<?xml version="1.0" encoding="UTF-8" ?>\n<savestates>\n')
    assert text.endswith('</savestates>\n')


def test_runtime_specs_carry_the_launcher_part(generated: Path) -> None:
    specs = json.loads((generated / 'savestates.json').read_text())

    assert specs['mame']['keys']['quick_save'] == ['KEY_LEFTSHIFT', 'KEY_F6']
    assert specs['mame']['autosave_file'] == '{{romfilename}}.quick.sta'
    assert specs['azahar']['mirror']['auto_slot'] == 0
    assert specs['duckstation']['mirror']['placement'] == [2, 10]
    assert specs['libretro']['directory'] == '{{system}}'
    assert 'keys' not in specs['libretro']


def test_an_overlay_replaces_the_spec(tmp_path: Path) -> None:
    (tmp_path / 'emu.emulator.yml').write_text('savestates:\n  directory: a\n  file: x\n')
    (tmp_path / 'extra.emu.emulator.yml').write_text('savestates:\n  directory: b\n')
    build(Registry.load_files([tmp_path / 'emu.emulator.yml', tmp_path / 'extra.emu.emulator.yml']), tmp_path)

    assert '<emulator name="emu"         directory="b" />' in (tmp_path / 'es_savestates.cfg').read_text()


def test_a_spec_needs_a_directory(tmp_path: Path) -> None:
    (tmp_path / 'emu.emulator.yml').write_text('savestates:\n  file: x\n')

    with pytest.raises(ValueError, match='directory'):
        build(Registry.load_files([tmp_path / 'emu.emulator.yml']), tmp_path)
