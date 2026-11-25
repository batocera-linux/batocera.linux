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
import os
import struct
import threading
import zipfile
import zlib
from itertools import count
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

import pytest

from batocera_common.paths import BIOS
from batocera_common.yaml import safe_load_yaml12
from batocera_launch.emulators.armsx2 import Armsx2
from batocera_launch.emulators.duckstation import Duckstation
from batocera_launch.plugin_manager import HookContext
from batocera_launch.plugins.savestates import SaveStatesPlugin
from batocera_launch.savestates import client, manager
from batocera_launch.savestates.manager import DONE, RESTART, UNHANDLED, SaveStateManager, release_state_manager
from batocera_launch.savestates.mirror import StateMirror
from batocera_launch.savestates.screenshots import duckstation_screenshot, encode_png
from batocera_launch.savestates.spec import AUTO, EsNaming, SaveStateSpec, load_spec

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture

    from batocera_launch import SystemConfig
    from batocera_launch.rom import Rom

_SPEC_KEYS: Final = {
    *('directory', 'file', 'image', 'nofileextension', 'firstslot', 'autosave', 'autosave_file', 'autosave_image'),
    *('incremental', 'slots', 'keys', 'boot', 'mirror', 'migrate', 'archive'),
}
_KEY_NAMES: Final = {
    *('quick_save', 'quick_load', 'save', 'restore', 'save_slot', 'load_slot', 'save_menu', 'load_menu', 'slot'),
}
_STEM = 'test'
_SERIAL = 'SLUS-00001'
_mtimes = count(1_000_000_000_000_000_000, 1_000_000_000)

type _Make = Callable[..., SaveStateManager]


def _save(path: Path, data: bytes, /) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    mtime = next(_mtimes)
    os.utime(path, ns=(mtime, mtime))


def _files(directory: Path, /) -> dict[str, bytes]:
    # the dot files are the mirror's records
    return {
        path.name: path.read_bytes()
        for path in sorted(directory.glob('*'))
        if path.is_file() and not path.name.startswith('.')
    }


def _duckstation(tmp_path: Path, /, **mirror: object) -> dict[str, Any]:
    return {
        'directory': str(tmp_path / 'es'),
        'file': '{{romfilename}}.{{slot0}}.sav',
        'autosave_file': '{{romfilename}}.auto.sav',
        'firstslot': 1,
        'slots': [1, 10],
        'keys': {
            'save': 'KEY_F2',
            'restore': 'KEY_F1',
            'save_slot': ['KEY_LEFTCTRL', 'KEY_LEFTSHIFT', 'KEY_F{slot}'],
            'load_slot': ['KEY_LEFTCTRL', 'KEY_F{slot}'],
        },
        'boot': {'args': ['-statefile', '{file}']},
        'mirror': {
            'native_dir': str(tmp_path / 'native'),
            'glob': '*.sav',
            'pattern': r'(?!savestate_\d+\.sav)(?P<serial>.+)_(?:(?P<slot>\d+)|resume)\.sav',
            'slot_name': '{serial}_{slot}.sav',
            'auto_name': '{serial}_resume.sav',
            'placement': [2, 10],
            'fresh': 1,
            **mirror,
        },
    }


@pytest.fixture
def make(
    mocker: MockerFixture, launch_config: SystemConfig, launch_config_user_settings: dict[str, str], tmp_path: Path
) -> _Make:
    def make(data: dict[str, Any], /, **settings: str) -> SaveStateManager:
        launch_config_user_settings.update(settings)
        spec = SaveStateSpec.from_dict({'directory': str(tmp_path / 'es'), **data})
        mocker.patch('batocera_launch.savestates.manager.load_spec', return_value=spec)
        state_manager = SaveStateManager(launch_config, spec)
        state_manager.prepare()
        return state_manager

    return make


@pytest.fixture
def send(mocker: MockerFixture) -> MagicMock:
    return mocker.patch('batocera_launch.savestates.manager.send_hotkey')


def _mirror(tmp_path: Path, /, **kwargs: Any) -> StateMirror:
    spec = SaveStateSpec.from_dict(_duckstation(tmp_path))
    assert spec.mirror is not None
    mirror = StateMirror(spec.mirror, spec.es, tmp_path / 'es', _STEM, **kwargs)
    mirror.prepare()
    return mirror


def _first_session(tmp_path: Path, /) -> None:
    native = tmp_path / 'native'
    _save(native / f'{_SERIAL}_1.sav', b'old')
    _save(native / 'SCUS-99999_1.sav', b'other game')

    mirror = _mirror(tmp_path)
    mirror.sync()
    _save(native / f'{_SERIAL}_2.sav', b'new')
    mirror.sync(final=True)
    mirror.write_record()


# naming and specs


@pytest.mark.parametrize(
    ('file', 'slot', 'name'),
    [
        ('{{romfilename}}.state{{slot}}', 0, 'test.state'),
        ('{{romfilename}}.state{{slot}}', 3, 'test.state3'),
        ('{{romfilename}}.s{{slot2d}}', 4, 'test.s04'),
        ('{{romfilename}}.{{slot0}}.sta', 0, 'test.0.sta'),
    ],
)
def test_es_names_round_trip(file: str, slot: int, name: str) -> None:
    naming = EsNaming(directory='x', file=file)

    assert naming.name('test', slot) == name
    assert naming.parse('test', name) == slot
    assert naming.parse('other', name) is None


def test_es_autosave_name() -> None:
    naming = EsNaming(directory='x', file='', autosave_file='{{romfilename}}.odinstate')

    assert naming.name('game', AUTO) == 'game.odinstate'
    assert naming.parse('game', 'game.odinstate') == AUTO
    assert naming.name('game', 1) is None


def test_es_directory_placeholders() -> None:
    naming = EsNaming(directory='{{system}}/{{core}}/states', file='')

    assert naming.directory_path('psx', 'duckstation', None) == Path('/userdata/saves/psx/duckstation/states')
    assert EsNaming(directory='/abs', file='').directory_path('a', 'b', 'c') == Path('/abs')


def test_specs_load_by_emulator(tmp_path: Path) -> None:
    path = tmp_path / 'savestates.json'
    path.write_text(json.dumps({'duckstation': _duckstation(tmp_path), 'broken': {'file': 'x'}}))

    spec = load_spec('duckstation', path)
    assert spec is not None
    assert spec.mirror is not None
    assert spec.mirror.placement == tuple(range(2, 11))
    assert spec.boot.args == ('-statefile', '{file}')
    assert load_spec('libretro', path) is None
    assert load_spec('broken', path) is None
    assert load_spec('duckstation', tmp_path / 'missing.json') is None


# the slot, booting from a state, migrations


def test_the_slot_es_asked_for_is_used(make: _Make) -> None:
    assert make({'slots': [1, 8]}, state_slot='3').slot == 3


def test_a_slot_past_the_emulator_takes_the_first_free_one(make: _Make, tmp_path: Path) -> None:
    for slot in (1, 2):
        _save(tmp_path / 'es' / f'test.ml{slot}', b'state')

    assert make({'file': '{{romfilename}}.ml{{slot0}}', 'slots': [1, 8]}, state_slot='12').slot == 3


def test_with_every_slot_used_the_oldest_is_taken(make: _Make, tmp_path: Path) -> None:
    for slot in (2, 0, 1):
        _save(tmp_path / 'es' / f'test_{slot}.dss', b'state')

    assert make({'file': '{{romfilename}}_{{slot0}}.dss', 'slots': [0, 2]}, state_slot='3').slot == 2


def test_boot_args_name_the_state(make: _Make) -> None:
    states = make({'boot': {'args': ['-statefile', '{file}']}}, state_filename='/s/test.2.sav')

    assert states.boot_args == ['-statefile', '/s/test.2.sav']
    assert make({'boot': {'args': ['-l', '{file}']}}, state_filename='').boot_args == []


_FLYCAST: dict[str, Any] = {
    'file': '{{romfilename}}_{{slot0}}.state',
    'slots': [1, 9],
    'keys': {'save': 'KEY_F9', 'restore': 'KEY_F8'},
    'boot': {'copy': True},
}


def test_the_current_slot_holds_the_newest_state(make: _Make, tmp_path: Path) -> None:
    for slot in (1, 3, 2):
        _save(tmp_path / 'es' / f'test_{slot}.state', b'state')

    states = make(_FLYCAST, state_slot='4')

    assert states.slot == 2
    assert not states.boot_in_slot


def test_starting_from_a_state_makes_its_slot_current(make: _Make, tmp_path: Path) -> None:
    for slot in (1, 2):
        _save(tmp_path / 'es' / f'test_{slot}.state', f'state {slot}'.encode())

    states = make(_FLYCAST, state_slot='3', state_filename=str(tmp_path / 'es' / 'test_1.state'))

    assert states.slot == 1
    assert states.boot_in_slot
    assert _files(tmp_path / 'es') == {'test_1.state': b'state 1', 'test_2.state': b'state 2'}


def test_a_state_elsewhere_is_copied_into_the_current_slot(make: _Make, tmp_path: Path) -> None:
    _save(tmp_path / 'other.state', b'chosen')

    states = make(_FLYCAST, state_slot='4', state_filename=str(tmp_path / 'other.state'))

    assert states.boot_in_slot
    assert (tmp_path / 'es' / 'test_4.state').read_bytes() == b'chosen'


def test_saving_in_the_current_slot_keeps_the_previous_state(make: _Make, send: MagicMock, tmp_path: Path) -> None:
    states = make(_FLYCAST, state_slot='1')
    states.hotkeys_context({'name': 'flycast', 'keys': {}})

    assert states.request('save') == DONE
    _save(tmp_path / 'es' / 'test_1.state', b'first')
    assert states.request('save') == DONE
    _save(tmp_path / 'es' / 'test_1.state', b'second')

    assert _files(tmp_path / 'es') == {'test_1.state': b'second', 'test_2.state': b'first'}
    assert [call.args[0] for call in send.call_args_list] == ['savestate_save', 'savestate_save']
    assert states.request('load', 1) == DONE
    assert states.request('load', 2) == RESTART


def test_mame_folders_named_after_the_game_flatten_into_the_system(make: _Make, tmp_path: Path) -> None:
    state = tmp_path / 'state'
    _save(state / 'test' / '1.sta', b'one')
    _save(state / 'test' / 'quick.sta', b'quick')
    _save(state / 'nes' / '1.sta', b'shared')
    _save(state / 'nes' / 'test.2.sta', b'two')
    _save(state / 'test' / '2.sta', b'kept')

    make(
        {
            'directory': str(state / 'nes'),
            'file': '{{romfilename}}.{{slot0}}.sta',
            'slots': [0, 9],
            'migrate': [
                {'from': '../{{romfilename}}/{{slot0}}.sta', 'to': '{{romfilename}}.{{slot0}}.sta'},
                {'from': '../{{romfilename}}/quick.sta', 'to': '{{romfilename}}.quick.sta'},
            ],
        }
    )

    assert _files(state / 'nes') == {
        '1.sta': b'shared',
        'test.1.sta': b'one',
        'test.2.sta': b'two',
        'test.quick.sta': b'quick',
    }
    assert _files(state / 'test') == {'2.sta': b'kept'}


def test_flycast_slot_zero_moves_to_slot_one_when_free(make: _Make, tmp_path: Path) -> None:
    data = {
        'file': '{{romfilename}}_{{slot0}}.state',
        'slots': [1, 9],
        'migrate': [{'from': '{{romfilename}}.state', 'to': '{{romfilename}}_1.state'}],
    }
    _save(tmp_path / 'es' / 'test.state', b'zero')
    make(data)
    assert _files(tmp_path / 'es') == {'test_1.state': b'zero'}

    _save(tmp_path / 'es' / 'test.state', b'another')
    make(data)
    assert _files(tmp_path / 'es') == {'test.state': b'another', 'test_1.state': b'zero'}


# hotkeys and requests


_MELONDS: dict[str, Any] = {
    'file': '{{romfilename}}.ml{{slot0}}',
    'firstslot': 1,
    'slots': [1, 8],
    'keys': {'save_slot': ['KEY_LEFTSHIFT', 'KEY_F{slot}'], 'load_slot': 'KEY_F{slot}'},
    'boot': {'send': 'load', 'delay': 0},
}

_MAME: dict[str, Any] = {
    'file': '{{romfilename}}.{{slot0}}.sta',
    'autosave_file': '{{romfilename}}.quick.sta',
    'slots': [0, 9],
    'keys': {
        'quick_save': ['KEY_LEFTSHIFT', 'KEY_F6'],
        'quick_load': ['KEY_LEFTSHIFT', 'KEY_F7'],
        'save_menu': 'KEY_F6',
        'load_menu': 'KEY_F7',
        'slot': 'KEY_{slot}',
    },
}


def test_per_slot_keys_cover_every_slot(make: _Make) -> None:
    actions = make(_MELONDS).hotkeys()

    assert actions['save_state'] == '/usr/bin/batocera-savestate save'
    assert actions['restore_state'] == '/usr/bin/batocera-savestate load'
    assert [actions[f'savestate_save_slot_{slot}'] for slot in range(1, 9)] == [
        ['KEY_LEFTSHIFT', f'KEY_F{slot}'] for slot in range(1, 9)
    ]
    assert actions['savestate_load_slot_8'] == 'KEY_F8'


def test_the_pad_keeps_the_quick_slot(make: _Make) -> None:
    actions = make(_MAME).hotkeys()

    assert actions['save_state'] == '/usr/bin/batocera-savestate save -1'
    assert actions['restore_state'] == '/usr/bin/batocera-savestate load -1'
    assert actions['savestate_quick_save'] == ['KEY_LEFTSHIFT', 'KEY_F6']


def test_a_state_the_emulator_only_boots_from_loads_by_restarting(make: _Make, tmp_path: Path) -> None:
    _save(tmp_path / 'es' / 'test.1.state', b'state')
    states = make(
        {'file': '{{romfilename}}.{{slot0}}.state', 'keys': {'save': 'KEY_F9'}, 'boot': {'args': ['-l', '{file}']}}
    )

    assert states.hotkeys()['restore_state'] == '/usr/bin/batocera-savestate load'
    states.hotkeys_context({'name': 'test', 'keys': {}})
    assert states.request('load') == RESTART


def test_launcher_keys_are_kept_and_save_keys_routed(make: _Make) -> None:
    states = make(_MELONDS)
    context = states.hotkeys_context({'name': 'melonds', 'keys': {'exit': 'KEY_ESC', 'save_state': 'KEY_F1'}})

    assert context['keys']['exit'] == 'KEY_ESC'
    assert context['keys']['save_state'] == '/usr/bin/batocera-savestate save'


def test_every_save_takes_a_new_slot(make: _Make, send: MagicMock, tmp_path: Path) -> None:
    _save(tmp_path / 'es' / 'test.ml1', b'state')
    states = make(_MELONDS)
    states.hotkeys_context({'name': 'melonds', 'keys': {}})

    for slot in (2, 3):
        assert states.request('save') == DONE
        _save(tmp_path / 'es' / f'test.ml{slot}', b'state')
    assert states.request('load') == DONE
    assert states.request('load', 1) == DONE
    assert states.request('load', 9) == RESTART

    assert [call.args[0] for call in send.call_args_list] == [
        'savestate_save_slot_2',
        'savestate_save_slot_3',
        'savestate_load_slot_3',
        'savestate_load_slot_1',
    ]


def test_with_every_slot_used_a_save_replaces_the_oldest(make: _Make, send: MagicMock, tmp_path: Path) -> None:
    for slot in (3, 1, 2, 4, 5, 6, 7, 8):
        _save(tmp_path / 'es' / f'test.ml{slot}', b'state')
    states = make(_MELONDS)
    states.hotkeys_context({'name': 'melonds', 'keys': {}})

    states.request('save')

    send.assert_called_once_with('savestate_save_slot_3')


def test_mame_numbered_states_go_through_the_menu_and_the_quick_slot_is_the_autosave(
    make: _Make, send: MagicMock, tmp_path: Path
) -> None:
    for slot in (0, 1):
        _save(tmp_path / 'es' / f'test.{slot}.sta', b'state')
    states = make(_MAME)
    states.hotkeys_context({'name': 'mame', 'keys': {}})

    assert states.request('save') == DONE
    assert states.request('save', -1) == DONE
    assert states.request('load', 1) == DONE
    assert states.request('load', 4) == RESTART
    assert states.request('load', -1) == DONE
    assert [call.args[0] for call in send.call_args_list] == [
        'savestate_save_menu',
        'savestate_slot_2',
        'savestate_quick_save',
        'savestate_load_menu',
        'savestate_slot_1',
        'savestate_quick_load',
    ]


def test_quick_slot_only_emulators_save_there(make: _Make, send: MagicMock) -> None:
    states = make(
        {'autosave_file': '{{romfilename}}.odinstate', 'keys': {'quick_save': 'KEY_F2', 'quick_load': 'KEY_F4'}}
    )
    states.hotkeys_context({'name': 'odin', 'keys': {}})

    assert states.request('save') == DONE
    assert states.request('load', -1) == DONE
    assert states.request('load', 1) == RESTART
    assert [call.args[0] for call in send.call_args_list] == ['savestate_quick_save', 'savestate_quick_load']


@pytest.mark.launch_rom_source('/userdata/roms/nds/Mario Kart DS (USA).zip')
def test_archive_roms_mirror_the_inner_name(make: _Make, mocker: MockerFixture, tmp_path: Path) -> None:
    inner = Path('0168 - Mario Kart DS (USA).nds')
    mocker.patch('batocera_launch.savestates.manager._archive_rom', return_value=inner)

    states = make({**_MELONDS, 'archive': ['nds']})
    assert states.mirror is not None
    _save(tmp_path / 'es' / '0168 - Mario Kart DS (USA).ml1', b'state')
    states.mirror.sync(final=True)

    assert _files(tmp_path / 'es')['Mario Kart DS (USA).ml1'] == b'state'


@pytest.mark.parametrize(
    ('names', 'inner'),
    [
        (['0168 - Mario Kart DS (USA).nds', 'readme.txt'], '0168 - Mario Kart DS (USA).nds'),
        (['dir/game.NDS'], 'game.NDS'),
        (['a.nds', 'b.nds'], None),
    ],
)
def test_the_rom_inside_a_zip(tmp_path: Path, names: list[str], inner: str | None) -> None:
    archive = tmp_path / 'game.zip'
    with zipfile.ZipFile(archive, 'w') as zip_file:
        for name in names:
            zip_file.writestr(name, b'data')

    assert manager._archive_rom(archive, ('nds',)) == (None if inner is None else Path(inner))
    assert manager._archive_rom(tmp_path / 'game.nds', ('nds',)) is None


def test_without_a_spec_the_launcher_keys_answer(make: _Make, send: MagicMock, launch_config: SystemConfig) -> None:
    states = SaveStateManager(launch_config, None)
    states.prepare()
    states.hotkeys_context({'name': 'dolphin', 'keys': {'load_state_slot_2': ['KEY_LEFTCTRL', 'KEY_F2']}})

    assert states.request('load', 2) == DONE
    assert states.request('load', 3) == UNHANDLED
    assert states.request('save') == UNHANDLED
    send.assert_called_once_with('load_state_slot_2')


def test_boot_sends_the_load_of_the_state_once_the_game_runs(make: _Make, send: MagicMock, tmp_path: Path) -> None:
    states = make(_MELONDS, state_filename=str(tmp_path / 'es' / 'test.ml4'))
    states.game_started()
    assert states._deferred is not None
    states._deferred.join()

    send.assert_called_once_with('savestate_load_slot_4')


def test_booting_from_the_quick_slot_loads_it(make: _Make, send: MagicMock, tmp_path: Path) -> None:
    data = {'autosave_file': '{{romfilename}}.auto.cst', 'keys': {'quick_load': 'KEY_F2', 'restore': 'KEY_V'}}
    states = make(
        {**data, 'boot': {'send': 'restore', 'delay': 0}}, state_filename=str(tmp_path / 'es' / 'test.auto.cst')
    )
    states.game_started()
    assert states._deferred is not None
    states._deferred.join()

    send.assert_called_once_with('savestate_quick_load')


def test_requests_reach_the_manager_over_the_socket(
    make: _Make, send: MagicMock, mocker: MockerFixture, tmp_path: Path
) -> None:
    path = Path('/tmp') / f'savestates-{os.getpid()}-{threading.get_ident()}.sock'
    mocker.patch.object(manager, 'SOCKET_PATH', path)
    states = make(_MELONDS)
    states.hotkeys_context({'name': 'melonds', 'keys': {}})
    states.start()

    try:
        assert client.request('save', path=path) == DONE
        assert client.request('load', '9', path=path) == RESTART
        assert client.request('save', '-1', path=path) == DONE
    finally:
        states.stop()

    assert not path.exists()
    assert client.request('save', path=path) == client.NO_LAUNCHER
    assert [call.args[0] for call in send.call_args_list] == ['savestate_save_slot_1', 'savestate_save_slot_2']


def test_a_stopping_launcher_leaves_a_later_launchs_socket(make: _Make, mocker: MockerFixture) -> None:
    path = Path('/tmp') / f'savestates-{os.getpid()}-{threading.get_ident()}.sock'
    mocker.patch.object(manager, 'SOCKET_PATH', path)
    old = make(_MELONDS)
    old.start()
    new = make(_MELONDS)
    new.hotkeys_context({'name': 'melonds', 'keys': {}})
    new.start()

    try:
        old.stop()
        assert client.request('load', '9', path=path) == RESTART
    finally:
        new.stop()

    assert not path.exists()


def test_plugin_runs_the_manager_for_any_emulator(mocker: MockerFixture, launch_config: SystemConfig) -> None:
    mocker.patch('batocera_launch.savestates.manager.load_spec', return_value=None)
    start = mocker.patch.object(SaveStateManager, 'start')
    stop = mocker.patch.object(SaveStateManager, 'stop')
    plugin = SaveStatesPlugin()
    context = HookContext(launch_config)

    plugin.start(context)
    plugin.stop(context)
    plugin.stop(context)

    start.assert_called_once()
    stop.assert_called_once()


# mirroring serial-named states


def test_first_session_learns_the_serial_and_links_its_states(tmp_path: Path) -> None:
    native = tmp_path / 'native'
    _save(native / f'{_SERIAL}_1.sav', b'old')
    _save(native / 'SCUS-99999_1.sav', b'other game')

    mirror = _mirror(tmp_path)
    mirror.sync()
    assert mirror.serials == []

    _save(native / f'{_SERIAL}_2.sav', b'new')
    mirror.sync()
    # not settled yet
    assert _files(tmp_path / 'es') == {}

    mirror.sync()
    assert mirror.serials == [_SERIAL]
    assert _files(tmp_path / 'es') == {f'{_STEM}.1.sav': b'old', f'{_STEM}.2.sav': b'new'}
    assert (tmp_path / 'es' / f'{_STEM}.2.sav').samefile(native / f'{_SERIAL}_2.sav')
    assert (native / 'SCUS-99999_1.sav').read_bytes() == b'other game'


def test_next_launch_rebuilds_the_slots_and_saves_a_new_state_where_es_asked(tmp_path: Path) -> None:
    _first_session(tmp_path)
    native = tmp_path / 'native'

    mirror = _mirror(tmp_path, state_slot=3)

    # slot 1 stays free for a new state, ES's states move up one
    assert not (native / f'{_SERIAL}_1.sav').exists()
    assert (native / f'{_SERIAL}_2.sav').read_bytes() == b'old'
    assert (native / f'{_SERIAL}_3.sav').read_bytes() == b'new'
    assert mirror.live_slots == {1: 2, 2: 3}

    _save(native / f'{_SERIAL}_1.sav', b'fresh')
    mirror.sync(final=True)

    assert _files(tmp_path / 'es')[f'{_STEM}.3.sav'] == b'fresh'


def test_overwriting_a_placed_slot_replaces_its_es_state(tmp_path: Path) -> None:
    _first_session(tmp_path)
    native = tmp_path / 'native'
    mirror = _mirror(tmp_path)

    # emulators write a temporary file and rename it over the state
    _save(native / 'tmp', b'overwritten')
    (native / 'tmp').replace(native / f'{_SERIAL}_2.sav')
    mirror.sync(final=True)

    assert _files(tmp_path / 'es')[f'{_STEM}.1.sav'] == b'overwritten'


def test_a_state_deleted_and_renumbered_in_es_stays_gone(tmp_path: Path) -> None:
    _first_session(tmp_path)
    es = tmp_path / 'es'
    (es / f'{_STEM}.1.sav').unlink()
    (es / f'{_STEM}.2.sav').rename(es / f'{_STEM}.1.sav')

    _mirror(tmp_path)

    native = tmp_path / 'native'
    assert sorted(path.name for path in native.glob(f'{_SERIAL}_*')) == [f'{_SERIAL}_2.sav']
    assert (native / f'{_SERIAL}_2.sav').read_bytes() == b'new'
    assert _files(es) == {f'{_STEM}.1.sav': b'new'}


def test_a_state_es_never_saw_is_imported_not_deleted(tmp_path: Path) -> None:
    _first_session(tmp_path)
    _save(tmp_path / 'native' / f'{_SERIAL}_7.sav', b'outside')

    _mirror(tmp_path)

    assert _files(tmp_path / 'es')[f'{_STEM}.3.sav'] == b'outside'


def test_states_are_copied_without_hard_links(tmp_path: Path, mocker: MockerFixture) -> None:
    mocker.patch('batocera_launch.savestates.mirror.os.link', side_effect=OSError)
    _first_session(tmp_path)

    assert _files(tmp_path / 'es') == {f'{_STEM}.1.sav': b'old', f'{_STEM}.2.sav': b'new'}
    assert not (tmp_path / 'es' / f'{_STEM}.2.sav').samefile(tmp_path / 'native' / f'{_SERIAL}_2.sav')

    # without links only the record tells a deleted state from a new one
    (tmp_path / 'es' / f'{_STEM}.1.sav').unlink()
    mirror = _mirror(tmp_path)

    assert _files(tmp_path / 'es') == {f'{_STEM}.2.sav': b'new'}
    _save(tmp_path / 'native' / f'{_SERIAL}_2.sav', b'rewritten')
    mirror.sync(final=True)
    assert _files(tmp_path / 'es') == {f'{_STEM}.2.sav': b'rewritten'}


def test_the_resume_state_is_the_es_autosave(tmp_path: Path) -> None:
    native = tmp_path / 'native'
    mirror = _mirror(tmp_path)
    _save(native / f'{_SERIAL}_resume.sav', b'on exit')
    mirror.sync(final=True)
    mirror.write_record()

    assert _files(tmp_path / 'es') == {f'{_STEM}.auto.sav': b'on exit'}

    (native / f'{_SERIAL}_resume.sav').unlink()
    _mirror(tmp_path)
    assert (native / f'{_SERIAL}_resume.sav').read_bytes() == b'on exit'


def test_the_state_es_starts_from_is_placed_first(make: _Make, send: MagicMock, tmp_path: Path) -> None:
    es = tmp_path / 'es'
    for slot in (1, 2, 3):
        _save(es / f'{_STEM}.{slot}.sav', f'state {slot}'.encode())
    _save(es / f'.{_STEM}.json', json.dumps({'serials': [_SERIAL], 'native': {}}).encode())
    data = _duckstation(tmp_path, placement=[1, 1], fresh=None)

    states = make(data, state_filename=str(es / f'{_STEM}.1.sav'))
    states.hotkeys_context({'name': 'duckstation', 'keys': {}})
    assert states.mirror is not None
    assert states.mirror.live_slots == {1: 1}
    assert (tmp_path / 'native' / f'{_SERIAL}_1.sav').read_bytes() == b'state 1'
    assert states.request('load', 1) == DONE
    assert states.request('load', 2) == RESTART
    send.assert_called_once_with('savestate_load_slot_1')


def test_load_without_a_slot_takes_the_newest_placed_state(make: _Make, send: MagicMock, tmp_path: Path) -> None:
    _first_session(tmp_path)
    states = make(_duckstation(tmp_path))
    states.hotkeys_context({'name': 'duckstation', 'keys': {}})

    assert states.request('load') == DONE
    # ES slot 2 was placed in the emulator's slot 3
    send.assert_called_once_with('savestate_load_slot_3')


def test_mirrored_saves_take_slots_without_a_state_of_the_game(make: _Make, send: MagicMock, tmp_path: Path) -> None:
    _first_session(tmp_path)
    states = make(_duckstation(tmp_path))
    states.hotkeys_context({'name': 'duckstation', 'keys': {}})

    states.request('save')
    states.request('save')

    # 2 and 3 hold the placed states
    assert [call.args[0] for call in send.call_args_list] == ['savestate_save_slot_1', 'savestate_save_slot_4']


def test_a_save_before_the_serial_is_known_keeps_clear_of_every_games_states(
    make: _Make, send: MagicMock, tmp_path: Path
) -> None:
    native = tmp_path / 'native'
    _save(native / f'{_SERIAL}_1.sav', b'legacy')
    _save(native / 'SCUS-99999_1.sav', b'other game')
    _save(native / 'SCUS-99999_2.sav', b'other game')
    states = make(_duckstation(tmp_path))
    states.hotkeys_context({'name': 'duckstation', 'keys': {}})

    states.request('save')
    _save(native / f'{_SERIAL}_3.sav', b'new')
    assert states.mirror is not None
    states.mirror.sync(final=True)

    assert [call.args[0] for call in send.call_args_list] == ['savestate_save_slot_3']
    assert _files(tmp_path / 'es') == {f'{_STEM}.1.sav': b'legacy', f'{_STEM}.3.sav': b'new'}


def test_the_native_folder_is_created(tmp_path: Path) -> None:
    _mirror(tmp_path)

    assert (tmp_path / 'native').is_dir()


def test_the_quick_slot_mirrors_to_the_autosave(tmp_path: Path) -> None:
    spec = SaveStateSpec.from_dict(
        {
            'directory': str(tmp_path / 'es'),
            'file': '{{romfilename}}.{{slot0}}.cst',
            'autosave_file': '{{romfilename}}.auto.cst',
            'firstslot': 1,
            'mirror': {
                'native_dir': str(tmp_path / 'native'),
                'glob': '*.cst',
                'pattern': r'(?P<serial>[0-9A-F]{16})\.(?P<slot>\d{2})\.cst',
                'slot_name': '{serial}.{slot:02d}.cst',
                'auto_slot': 0,
                'placement': [1, 1],
            },
        }
    )
    assert spec.mirror is not None
    mirror = StateMirror(spec.mirror, spec.es, tmp_path / 'es', _STEM)
    mirror.prepare()
    _save(tmp_path / 'native' / '0004000000055D00.00.cst', b'quick')
    _save(tmp_path / 'native' / '0004000000055D00.01.cst', b'one')
    mirror.sync(final=True)
    mirror.write_record()

    assert _files(tmp_path / 'es') == {f'{_STEM}.auto.cst': b'quick', f'{_STEM}.1.cst': b'one'}

    StateMirror(spec.mirror, spec.es, tmp_path / 'es', _STEM).prepare()
    assert (tmp_path / 'native' / '0004000000055D00.00.cst').read_bytes() == b'quick'


def test_screenshots_sit_next_to_the_es_state(tmp_path: Path, mocker: MockerFixture) -> None:
    def screenshot(path: Path, /) -> bytes:
        return b'png'

    mocker.patch.dict('batocera_launch.savestates.mirror.SCREENSHOTS', {'test': screenshot})
    spec = SaveStateSpec.from_dict(_duckstation(tmp_path, screenshot='test'))
    assert spec.mirror is not None
    mirror = StateMirror(spec.mirror, spec.es, tmp_path / 'es', _STEM)
    mirror.prepare()
    _save(tmp_path / 'native' / f'{_SERIAL}_1.sav', b'state')
    mirror.sync(final=True)

    assert (tmp_path / 'es' / f'{_STEM}.1.sav.png').read_bytes() == b'png'


@pytest.mark.parametrize(
    ('name', 'parsed'),
    [
        ('SLUS-00001_10.sav', ('SLUS-00001', 10)),
        ('SLUS-00001_resume.sav', ('SLUS-00001', AUTO)),
        ('savestate_1.sav', None),
        ('resume.sav', None),
    ],
)
def test_duckstation_native_names(tmp_path: Path, name: str, parsed: tuple[str, int] | None) -> None:
    spec = SaveStateSpec.from_dict(_duckstation(tmp_path))
    assert spec.mirror is not None

    assert spec.mirror.parse(name) == parsed
    if parsed is not None:
        assert spec.mirror.native_name(*parsed) == name


# screenshots


def test_duckstation_screenshot_becomes_a_png(tmp_path: Path) -> None:
    width, height = 2, 1
    pixels = bytes([255, 0, 0, 0, 0, 255, 0, 0])
    compressed = zlib.compress(pixels)
    header = bytearray(200)
    struct.pack_into('<II', header, 0, 0x43435544, 69)
    struct.pack_into('<5I', header, 180, 1, width, height, len(compressed), 200)
    state = tmp_path / 'SLUS-00001_1.sav'
    state.write_bytes(bytes(header) + compressed)

    png = duckstation_screenshot(state)

    assert png is not None
    assert png.startswith(b'\x89PNG\r\n\x1a\n')
    assert struct.unpack_from('>II', png, 16) == (width, height)
    idat = png.index(b'IDAT')
    (length,) = struct.unpack_from('>I', png, idat - 4)
    assert zlib.decompress(png[idat + 4 : idat + 4 + length]) == b'\0\xff\x00\x00\x00\xff\x00'


def test_encode_png_drops_alpha() -> None:
    png = encode_png(1, 1, b'\x01\x02\x03\x00')
    idat = png.index(b'IDAT')
    (length,) = struct.unpack_from('>I', png, idat - 4)
    assert zlib.decompress(png[idat + 4 : idat + 4 + length]) == b'\0\x01\x02\x03'


# launchers


@pytest.fixture
def boot_spec(mocker: MockerFixture, launch_config: SystemConfig) -> Iterator[None]:
    spec = SaveStateSpec.from_dict({'directory': '/userdata/saves/x', 'boot': {'args': ['-statefile', '{file}']}})
    mocker.patch('batocera_launch.savestates.manager.load_spec', return_value=spec)
    yield
    release_state_manager(launch_config)


@pytest.mark.launch_config_emulator('duckstation')
@pytest.mark.launch_config_system('psx')
@pytest.mark.launch_config_user_settings({'state_slot': '3', 'state_filename': '/userdata/saves/psx/test.2.sav'})
@pytest.mark.usefixtures('fake_fs', 'boot_spec')
async def test_duckstation_starts_from_the_es_state(
    mocker: MockerFixture, launch_config: SystemConfig, launch_rom: Rom
) -> None:
    mocker.patch.object(Duckstation, '_write_settings')
    emulator = Duckstation(config=launch_config, profiler=mocker.Mock())
    emulator.rom = launch_rom

    command = await emulator.configure()

    assert command.args[-4:] == ['-statefile', '/userdata/saves/psx/test.2.sav', '--', launch_rom]


@pytest.mark.launch_config_emulator('armsx2')
@pytest.mark.launch_config_system('ps2')
@pytest.mark.launch_config_user_settings({'state_slot': '3', 'state_filename': '/userdata/saves/ps2/test.2.p2s'})
@pytest.mark.usefixtures('fake_fs', 'boot_spec')
async def test_armsx2_takes_no_state_index(mocker: MockerFixture, launch_config: SystemConfig, launch_rom: Rom) -> None:
    mocker.patch.object(Armsx2, '_configure_reg')
    mocker.patch.object(Armsx2, '_configure_ini')
    mocker.patch.object(Armsx2, '_configure_audio')
    mocker.patch.object(Armsx2, 'get_sdl_game_controller_config', return_value='')
    mocker.patch('batocera_launch.emulators.armsx2.configure_emulator', return_value=False)
    (BIOS / 'ps2').mkdir(parents=True)
    (BIOS / 'ps2' / 'patches.zip').touch()
    emulator = Armsx2(config=launch_config, profiler=mocker.Mock())
    emulator.rom = launch_rom

    command = await emulator.configure()

    assert '-stateindex' not in command.args
    assert command.args[-2:] == ['-statefile', '/userdata/saves/ps2/test.2.p2s']


_REPO_SPECS: Final = sorted(
    path
    for path in (Path(__file__).resolve().parents[3] / 'package' / 'batocera').rglob('*.emulator.yml')
    if 'savestates:' in path.read_text()
)


@pytest.mark.parametrize('path', _REPO_SPECS, ids=[path.name for path in _REPO_SPECS])
def test_every_emulator_spec_loads(path: Path) -> None:
    data = safe_load_yaml12(path, dict[str, Any])
    assert data is not None

    spec = SaveStateSpec.from_dict(data['savestates'])

    assert set(data['savestates']) <= _SPEC_KEYS
    assert set(spec.keys) <= _KEY_NAMES
    if spec.keys.keys() & {'save_slot', 'load_slot', 'save_menu'}:
        assert spec.slots is not None
    if 'quick_save' in spec.keys:
        assert spec.es.autosave_file is not None


def test_the_spec_set_is_complete() -> None:
    assert {path.name.split('.')[0] for path in _REPO_SPECS} >= {
        'armsx2', 'azahar', 'dolphin', 'drastic', 'duckstation', 'flycast', 'keisho', 'libretro', 'mame',
        'melonds', 'mupen64plus', 'nanoboyadvance', 'odin', 'pcsx2', 'ppsspp', 'rpcs3',
    }  # fmt: skip
