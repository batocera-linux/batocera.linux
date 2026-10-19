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

from typing import TYPE_CHECKING, Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import SAVES
from batocera_launch import Command, Controller, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_launch import Controllers

_KEYMAPPING: Final[dict[str, str | None]] = {
    'button_up': None,
    'button_down': None,
    'button_left': None,
    'button_right': None,
    'button_action': 'a',
    'button_cancel': 'b',
    'button_shift': 'pageup',
    'button_n0': None,
    'button_n1': None,
    'button_n2': None,
    'button_n3': None,
    'button_n4': None,
    'button_n5': None,
    'button_n6': None,
    'button_n7': None,
    'button_n8': None,
    'button_n9': None,
    'button_plus': None,
    'button_minus': None,
    'button_multiply': None,
    'button_divide': None,
    'button_period': None,
    'button_debug_menu': None,
    'button_debug_through': None,
}


def _write_pad_config(config_dir: Path, controllers: Controllers, /) -> None:
    with (config_dir / 'config.ini').open('w', encoding='ascii') as f:
        f.write('[Joypad]\n')
        if pad := Controller.find_player_number(controllers, 1):
            f.write(f'number={pad.index}\n')
            for key, value in _KEYMAPPING.items():
                button: str | int = -1
                if value is not None and pad.inputs[value].type == 'button':
                    button = pad.inputs[value].id
                f.write(f'{key}={button}\n')


@cached_dataclass
class EasyRPG(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'easyrpg',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_F1',
                'pause': 'KEY_ESC',
                'save_state': 'KEY_F11',
                'fastforward': 'KEY_F',
            },
        }

    @cached_property
    def saves_dir(self) -> Path:
        return SAVES / 'easyrpg' / self.rom.name

    async def configure(self) -> Command:
        args: list[str | Path] = ['easyrpg-player']

        if self.config.show_fps:
            args.append('--show-fps')

        if self.config.get_bool('testplay'):
            args.append('--test-play')

        encoding = self.config.get_str('encoding', 'auto')
        args.extend(['--encoding', 'auto' if encoding == 'autodetect' else encoding])

        self.saves_dir.mkdir(parents=True, exist_ok=True)
        args.extend(['--save-path', self.saves_dir])

        self.config_dir.mkdir(parents=True, exist_ok=True)
        args.extend(['--project-path', self.rom])

        _write_pad_config(self.config_dir, self.controllers)

        return Command(args)
