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

import shutil
from pathlib import Path
from typing import Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import SCREENSHOTS
from batocera_launch import Command, Controller, Emulator, HotkeysContext

_SYSTEM_DIR: Final = Path('/usr/share/sdlpop')
_SCREENSHOTS_DIR: Final = SCREENSHOTS / 'sdlpop'


@cached_dataclass
class SdlPop(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'sdlpop',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_ESC',
                'pause': 'KEY_ESC',
                'save_state': 'KEY_F6',
                'restore_state': 'KEY_F9',
                'reset': ['KEY_LEFTCTRL', 'KEY_R'],
            },
        }

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)

        user_config = self.config_dir / 'SDLPoP.cfg'
        user_ini = self.config_dir / 'SDLPoP.ini'
        system_cfg = _SYSTEM_DIR / 'cfg' / 'SDLPoP.cfg'
        system_ini_src = _SYSTEM_DIR / 'cfg' / 'SDLPoP.ini'

        if not user_config.exists():
            shutil.copyfile(system_cfg, user_config)
        if not user_ini.exists():
            shutil.copyfile(system_ini_src, user_ini)

        system_config = _SYSTEM_DIR / 'SDLPoP.cfg'
        system_ini = _SYSTEM_DIR / 'SDLPoP.ini'
        if not system_config.exists():
            system_config.symlink_to(user_config)
        if not system_ini.exists():
            system_ini.symlink_to(user_ini)

        if not _SCREENSHOTS_DIR.exists():
            _SCREENSHOTS_DIR.mkdir(parents=True)
            (_SYSTEM_DIR / 'screenshots').symlink_to(_SCREENSHOTS_DIR, target_is_directory=True)

        args: list[str | Path] = ['SDLPoP']
        if pad := Controller.find_player_number(self.controllers, 1):
            args.append(f'joynum={pad.index}')

        return Command(args)
