from __future__ import annotations

import shutil
from pathlib import Path
from typing import Final

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import ROMS
from batocera_launch import (
    Command,
    Emulator,
    HotkeysContext,
)

_BINARY_SRC: Final = Path('/usr/bin/sonic-mania')


@cached_dataclass
class SonicMania(Emulator):
    needs_sdl_game_controller_config = True
    needs_sdl_controller_db = True

    @cached_property
    def sdl_controller_db_path(self) -> Path:
        return self.roms_dir / 'gamecontrollerdb.txt'

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'sonic_mania',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_ENTER',
                'pause': 'KEY_ENTER',
            },
        }

    @cached_property
    def roms_dir(self) -> Path:
        return ROMS / 'sonic-mania'

    @property
    def execution_path(self) -> Path | None:
        return self.roms_dir

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    async def configure(self) -> Command:
        destination_file = self.roms_dir / 'sonic-mania'
        if not destination_file.exists():
            shutil.copy(_BINARY_SRC, destination_file)

        config = CaseSensitiveConfigParser(interpolation=None)
        config['Game'] = {
            'devMenu': 'y',
            'faceButtonFlip': 'n',
            'enableControllerDebugging': 'n',
            'disableFocusPause': 'n',
            'region': '-1',
            'language': self.config.get_str('smania_language', '0'),
        }
        config['Video'] = {
            'windowed': 'n',
            'border': 'n',
            'exclusiveFS': 'y',
            'vsync': self.config.get_str('smania_vsync', 'y'),
            'tripleBuffering': self.config.get_str('smania_buffering', 'n'),
            'winWidth': '848',
            'winHeight': '480',
            'refreshRate': '60',
            'shaderSupport': 'y',
            'screenShader': '1',
            'maxPixWidth': '0',
        }
        config['Audio'] = {
            'streamsEnabled': 'y',
            'streamVolume': '1.000000',
            'sfxVolume': '1.000000',
        }

        with (self.roms_dir / 'Settings.ini').open('w') as configfile:
            config.write(configfile)

        return Command(
            [destination_file],
            env={'SDL_JOYSTICK_HIDAPI': '0'},
        )
