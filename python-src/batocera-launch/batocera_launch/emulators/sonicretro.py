from __future__ import annotations

import hashlib
from functools import cache
from typing import TYPE_CHECKING, Final

from batocera_common.configparser import CaseSensitiveRawConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import (
    Command,
    Controller,
    Emulator,
    HotkeysContext,
)

if TYPE_CHECKING:
    from pathlib import Path

_SONIC_BUTTONS: Final = {
    'Up': '11',
    'Down': '12',
    'Left': '13',
    'Right': '14',
    'A': '0',
    'B': '1',
    'C': '2',
    'X': '3',
    'Y': '22',
    'Z': '23',
    'L': '9',
    'R': '10',
    'Select': '4',
    'Start': '6',
}

_SONIC_KEYS: Final = {
    'Up': '82',
    'Down': '81',
    'Left': '80',
    'Right': '79',
    'A': '29',
    'B': '27',
    'C': '6',
    'X': '4',
    'Y': '22',
    'Z': '7',
    'L': '20',
    'R': '8',
    'Start': '40',
    'Select': '43',
}

_ORIGINS_GAME_CONFIG: Final = {
    # Sonic 1
    '5250b0e2effa4d48894106c7d5d1ad32',
    '5771433883e568715e7ac994bb22f5ed',
    # Sonic 2
    'f958285af4a09d2023b4e4f453691c4f',
    '9fe2dae0a8a2c7d8ef0bed639b3c749f',
    # Sonic CD
    'e723aab26026e4e6d4522c4356ef5a98',
}

_MOUSE_ROMS: Final = {
    '1bd5ad366df1765c98d20b53c092a528',  # iOS version of SonicCD
}


@cache
def _get_resolved_path_md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes(), usedforsecurity=False).hexdigest()


def _get_path_md5(path: Path) -> str:
    return _get_resolved_path_md5(path.resolve())


@cached_dataclass
class SonicRetro(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'sonicretro',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_ENTER',
                'pause': 'KEY_ENTER',
            },
        }

    @property
    def execution_path(self) -> Path | None:
        return self.rom

    @property
    def needs_mouse(self) -> bool:
        if self.rom.name.lower().endswith('son'):
            return False
        data_file = self.rom / 'Data.rsdk'
        return data_file.is_file() and _get_path_md5(data_file) in _MOUSE_ROMS

    async def configure(self) -> Command:
        emu = 'sonic2013' if self.rom.name.lower().endswith('son') else 'soniccd'
        ini_file = self.rom / 'settings.ini'

        if ini_file.exists():
            ini_file.unlink()

        sonic_config = CaseSensitiveRawConfigParser(strict=False)

        sonic_config.add_section('Dev')
        sonic_config.set('Dev', 'DevMenu', self.config.get_bool('devmenu', return_values=('true', 'false')))
        sonic_config.set('Dev', 'EngineDebugMode', 'false')
        if emu == 'sonic2013':
            sonic_config.set('Dev', 'StartingCategory', '255')
            sonic_config.set('Dev', 'StartingScene', '255')
            sonic_config.set('Dev', 'StartingPlayer', '255')
            sonic_config.set('Dev', 'StartingSaveFile', '255')
        else:
            sonic_config.set('Dev', 'StartingCategory', '0')
            sonic_config.set('Dev', 'StartingScene', '0')
            sonic_config.set('Dev', 'UseSteamDir', 'false')
        sonic_config.set('Dev', 'FastForwardSpeed', '8')
        sonic_config.set('Dev', 'UseHQModes', self.config.get_bool('hqmode', True, return_values=('true', 'false')))
        sonic_config.set('Dev', 'DataFile', 'Data.rsdk')

        sonic_config.add_section('Game')
        if emu == 'sonic2013':
            sonic_config.set(
                'Game', 'SkipStartMenu', self.config.get_bool('skipstart', return_values=('true', 'false'))
            )
        else:
            sonic_config.set('Game', 'OriginalControls', self.config.get_str('spindash', '-1'))
            sonic_config.set('Game', 'DisableTouchControls', 'true')

        game_config_bin = self.rom / 'Data' / 'Game' / 'GameConfig.bin'
        if game_config_bin.is_file() and _get_path_md5(game_config_bin) in _ORIGINS_GAME_CONFIG:
            sonic_config.set('Game', 'GameType', '1')

        sonic_config.set('Game', 'Language', self.config.get_str('language', '0'))

        sonic_config.add_section('Window')
        sonic_config.set('Window', 'FullScreen', 'true')
        sonic_config.set('Window', 'Borderless', 'true')
        sonic_config.set('Window', 'VSync', self.config.get_bool('vsync', True, return_values=('true', 'false')))
        sonic_config.set('Window', 'ScalingMode', self.config.get_str('scalingmode', '2'))
        sonic_config.set('Window', 'WindowScale', '2')
        sonic_config.set('Window', 'ScreenWidth', '424')
        sonic_config.set('Window', 'RefreshRate', '60')
        sonic_config.set('Window', 'DimLimit', '-1')

        sonic_config.add_section('Audio')
        sonic_config.set('Audio', 'BGMVolume', '1.000000')
        sonic_config.set('Audio', 'SFXVolume', '1.000000')

        sonic_config.add_section('Keyboard 1')
        for name, key in _SONIC_KEYS.items():
            sonic_config.set('Keyboard 1', name, key)

        sonic_config.add_section('Controller 1')
        if Controller.find_player_number(self.controllers, 1):
            for name, button in _SONIC_BUTTONS.items():
                sonic_config.set('Controller 1', name, button)

        with ini_file.open('w') as configfile:
            sonic_config.write(configfile, space_around_delimiters=False)

        return Command([emu])
