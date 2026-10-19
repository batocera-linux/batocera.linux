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

import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

from batocera_launch.cli.arguments import PlayerArguments
from batocera_launch.devices.controller import Controller
from batocera_launch.paths import ES_PLAYERS_INPUT, SYSTEM_ES_DIR

if TYPE_CHECKING:
    from pathlib import Path

    from pyfakefs.fake_filesystem import FakeFilesystem
    from pytest_mock import MockerFixture

_NAME = 'Test Pad'
_GUID = '03000000aaaa0000bbbb000001000000'


def _input_list(button_id: str, /) -> str:
    return (
        '<inputList>'
        f'<inputConfig type="joystick" deviceName="{_NAME}" deviceGUID="{_GUID}">'
        f'<input name="a" type="button" id="{button_id}" value="1" />'
        '</inputConfig>'
        '</inputList>'
    )


def _write(path: Path, text: str, /) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _player() -> PlayerArguments:
    return PlayerArguments(
        index=0, guid=_GUID, name=_NAME, devicepath='/dev/input/event3', nbbuttons=12, nbhats=1, nbaxes=6
    )


def test_uses_the_configs_es_resolved_without_reading_es_input(fs: FakeFilesystem, mocker: MockerFixture) -> None:
    _write(ES_PLAYERS_INPUT, _input_list('7'))
    _write(SYSTEM_ES_DIR / 'es_input.cfg', _input_list('0'))
    parse = mocker.spy(ET, 'parse')

    (controller,) = Controller.load_for_players([_player()])

    assert controller.inputs['a'].id == '7'
    assert [str(call.args[0]) for call in parse.call_args_list] == [str(ES_PLAYERS_INPUT)]


def test_falls_back_to_es_input_without_the_players_file(fs: FakeFilesystem) -> None:
    _write(SYSTEM_ES_DIR / 'es_input.cfg', _input_list('0'))

    (controller,) = Controller.load_for_players([_player()])

    assert controller.inputs['a'].id == '0'
