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
from batocera_launch import Command, Controller, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_launch import Controllers

_BUTTONS: Final = {
    'action': 'b',
    'attack': 'a',
    'item1': 'x',
    'item2': 'y',
    'pause': 'start',
}

_DIRECTIONS: Final = {
    'dpad': {'up': 'dpad_up', 'down': 'dpad_down', 'left': 'dpad_left', 'right': 'dpad_right'},
    'joystick1': {'up': 'left_y -', 'down': 'left_y +', 'left': 'left_x -', 'right': 'left_x +'},
    'joystick2': {'up': 'right_y -', 'down': 'right_y +', 'left': 'right_x -', 'right': 'right_x +'},
}


def _write_pad_config(config_dir: Path, controllers: Controllers, joystick: str | None, /) -> None:
    config_dir.mkdir(parents=True, exist_ok=True)
    with (config_dir / 'pads.ini').open('w', encoding='ascii') as f:
        if Controller.find_player_number(controllers, 1):
            bindings = _BUTTONS | _DIRECTIONS.get(joystick or '', _DIRECTIONS['dpad'])
            f.writelines(f'{key}={value}\n' for key, value in bindings.items())


@cached_dataclass
class Solarus(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'solarus',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    async def configure(self) -> Command:
        args: list[str | Path] = ['solarus-run', '-fullscreen=yes', '-cursor-visible=no', '-lua-console=no']

        for nplayer, pad in enumerate(self.controllers, start=1):
            if nplayer == 1 and 'hotkey' in pad.inputs and 'start' in pad.inputs:
                args.append(f'-quit-combo={pad.inputs["hotkey"].id}+{pad.inputs["start"].id}')
            args.append(f'-joypad-num{nplayer}={pad.index}')

        _write_pad_config(self.config_dir, self.controllers, self.config.get_str('joystick'))

        args.append(self.rom)

        return Command(
            args,
            env={
                'SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS': '0',
                'SDL_JOYSTICK_HIDAPI': '0',
            },
        )
