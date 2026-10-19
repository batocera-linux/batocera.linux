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

from typing import TYPE_CHECKING

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import (
    Command,
    Emulator,
    HotkeysContext,
)

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class DosBox(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'dosbox',
            'keys': {'exit': ['KEY_LEFTCTRL', 'KEY_F9']},
        }

    async def configure(self) -> Command:
        bat_file = self.rom / 'dosbox.bat'
        game_conf_file = self.rom / 'dosbox.cfg'

        self.config_dir.mkdir(parents=True, exist_ok=True)

        ini_settings = CaseSensitiveConfigParser(interpolation=None)

        # Use a separate file from dosbox.conf to avoid overwriting by dosbox
        custom_config_path = self.config_dir / 'dosbox-custom.conf'
        if custom_config_path.exists():
            ini_settings.read(custom_config_path)

        if not ini_settings.has_section('sdl'):
            ini_settings.add_section('sdl')
        ini_settings.set('sdl', 'output', 'opengl')

        if not ini_settings.has_section('cpu'):
            ini_settings.add_section('cpu')

        # loaded after the game's dosbox.cfg, so only override it when an option is set
        for key in ('core', 'cputype', 'cycles'):
            if value := self.config.get_str(f'dosbox_cpu_{key}'):
                ini_settings.set('cpu', key, value)
            else:
                ini_settings.remove_option('cpu', key)

        with custom_config_path.open('w') as config:
            ini_settings.write(config)

        args: list[str | Path] = [
            '/usr/bin/dosbox',
            '-fullscreen',
            # This loads self.config_dir / dosbox.conf
            '-userconf',
            '-exit',
            bat_file,
            '-c',
            f'set ROOT={self.rom}',
        ]

        if game_conf_file.exists():
            # Then load game_conf_file if it exists
            args.extend(['-conf', game_conf_file])

        # Then load custom_config_path after all the others
        args.extend(['-conf', custom_config_path])

        return Command(args)
