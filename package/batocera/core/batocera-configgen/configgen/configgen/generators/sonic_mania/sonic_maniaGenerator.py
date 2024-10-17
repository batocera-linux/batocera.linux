from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import ROMS
from ...controller import generate_sdl_game_controller_config
from ...utils.configparser import CaseSensitiveConfigParser
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

class SonicManiaGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "sonic_mania",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_ENTER", "pause": "KEY_ENTER" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        source_file = Path('/usr/bin/sonic-mania')
        rom_directory = ROMS / 'sonic-mania'
        destination_file = rom_directory / 'sonic-mania'

        if not destination_file.exists():
            shutil.copy(source_file, destination_file)

        ## Configuration

        # VSync
        if system.isOptSet('smania_vsync'):
            selected_vsync = system.config['smania_vsync']
        else:
            selected_vsync = 'y'
        # Triple Buffering
        if system.isOptSet('smania_buffering'):
            selected_buffering = system.config['smania_buffering']
        else:
            selected_buffering = 'n'
        # Language
        if system.isOptSet('smania_language'):
            selected_language = system.config['smania_language']
        else:
            selected_language = '0'

        ## Create the Settings.ini file
        config = CaseSensitiveConfigParser()

        # Game
        config['Game'] = {
            'devMenu': 'y',
            'faceButtonFlip': 'n',
            'enableControllerDebugging': 'n',
            'disableFocusPause': 'n',
            'region': '-1',
            'language': selected_language
        }
        # Video
        config['Video'] = {
            'windowed': 'n',
            'border': 'n',
            'exclusiveFS': 'y',
            'vsync': selected_vsync,
            'tripleBuffering': selected_buffering,
            'winWidth': '848',
            'winHeight': '480',
            'refreshRate': '60',
            'shaderSupport': 'y',
            'screenShader': '1',
            'maxPixWidth': '0'
        }
        # Audio
        config['Audio'] = {
            'streamsEnabled': 'y',
            'streamVolume': '1.000000',
            'sfxVolume': '1.000000'
        }
        # Save the ini file
        with (rom_directory / 'Settings.ini').open('w') as configfile:
            config.write(configfile)

        # Now run
        os.chdir(rom_directory)
        commandArray = [destination_file]

        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    # Show mouse for menu / play actions
    def getMouseMode(self, config, rom):
        return False

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
