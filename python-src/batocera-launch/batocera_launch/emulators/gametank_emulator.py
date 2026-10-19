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
from batocera_common.paths import CONFIGS
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path

_PALETTES: Final = frozenset({'capture', 'contrast', 'hdmi', 'legacy'})


@cached_dataclass
class GametankEmulator(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'gametank-emulator',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_ESC',
                'reset': 'KEY_R',
                'fastforward': 'KEY_GRAVE',
                'screenshot': 'KEY_F8',
            },
        }

    @cached_property
    def in_game_ratio(self) -> float:
        return 4 / 3

    async def configure(self) -> Command:
        args: list[str | Path] = ['gametank-emulator', '--fullscreen']

        if (palette := self.config.get_str('gametank_palette', 'capture')) in _PALETTES:
            args.append(f'--palette={palette}')

        if self.config.get_str('gametank_renderer') == 'software':
            args.append('--softrender')

        if self.config.get_bool('gametank_instantblits'):
            args.append('--instantblits')

        if self.config.get_bool('gametank_paddle'):
            args.append('--paddle')

        if not self.config.get_bool('gametank_sound', True):
            args.append('--nosound')

        args.append(self.rom)

        # the emulator keeps its pad bindings under $XDG_DATA_HOME/GameTank
        return Command(args, env={'XDG_DATA_HOME': CONFIGS})
