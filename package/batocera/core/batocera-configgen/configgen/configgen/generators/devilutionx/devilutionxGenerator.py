from __future__ import annotations

import configparser
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, SAVES
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


class DevilutionXGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        configDir = CONFIGS / 'devilutionx'
        configFile = configDir / 'diablo.ini'
        saveDir = SAVES / 'devilutionx'

        configDir.mkdir(parents=True, exist_ok=True)
        saveDir.mkdir(parents=True, exist_ok=True)

        ## Configure
        config = configparser.ConfigParser()

        if configFile.exists():
            config.read(configFile)

        # Ensure the [Graphics] section exists
        if 'Graphics' not in config:
            config['Graphics'] = {}

        config['Graphics']['Fit to Screen'] = system.config.get_bool("devilutionx_stretch", return_values=("1", "0"))

        with configFile.open('w') as file:
            config.write(file)

        commandArray = [
            'devilutionx', '--data-dir', '/userdata/roms/devilutionx',
            '--config-dir', configDir, '--save-dir', saveDir
        ]
        if rom.name.endswith('hellfire.mpq'):
            commandArray.append('--hellfire')
        elif rom.name.endswith('spawn.mpq'):
            commandArray.append('--spawn')
        else:
            commandArray.append('--diablo')

        if system.config.show_fps:
            commandArray.append('-f')

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers)
            }
        )

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "devilutionx",
            "keys": {
                "exit": ["KEY_LEFTALT", "KEY_F4"],
                "menu": "KEY_ESC",
                "pause": "KEY_ESC",
                "save_state": "KEY_F2",
                "restore_state": "KEY_F3"
            }
        }

    def getInGameRatio(self, config, gameResolution, rom):
        if config.get_bool("devilutionx_stretch"):
            return 16 / 9
        return 4 / 3
