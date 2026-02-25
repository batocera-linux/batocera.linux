from __future__ import annotations

import configparser
from typing import TYPE_CHECKING, Final

from batocera_common.paths import ROMS
from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

if TYPE_CHECKING:
    from pathlib import Path

_DATA_DIR: Final = ROMS / 'devilutionx'


@cached_dataclass
class DevilutionX(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'devilutionx',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_ESC',
                'pause': 'KEY_ESC',
                'save_state': 'KEY_F2',
                'restore_state': 'KEY_F3',
            },
        }

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9 if self.config.get_bool('devilutionx_stretch') else 4 / 3

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.saves_dir.mkdir(parents=True, exist_ok=True)

        config = configparser.ConfigParser()
        config_file = self.config_dir / 'diablo.ini'

        if config_file.exists():
            config.read(config_file)

        if 'Graphics' not in config:
            config['Graphics'] = {}

        config['Graphics']['Fit to Screen'] = self.config.get_bool('devilutionx_stretch', return_values=('1', '0'))

        with config_file.open('w') as file:
            config.write(file)

        command: list[str | Path] = [
            'devilutionx',
            '--data-dir',
            _DATA_DIR,
            '--config-dir',
            self.config_dir,
            '--save-dir',
            self.saves_dir,
        ]

        if self.rom.name.endswith('hellfire.mpq'):
            command.append('--hellfire')
        elif self.rom.name.endswith('spawn.mpq'):
            command.append('--spawn')
        else:
            command.append('--diablo')

        if self.config.show_fps:
            command.append('-f')

        return Command(command)
