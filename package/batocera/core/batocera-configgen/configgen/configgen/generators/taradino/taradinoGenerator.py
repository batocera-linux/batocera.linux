import configparser
import os

from ...batoceraPaths import CONFIGS
from ... import Command
from ... import controllersConfig
from ..Generator import Generator

class TaradinoGenerator(Generator):

    def getHotkeysContext(self):
        return {
            "name": "taradino",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        commandArray = [ "taradino" ]

        return Command.Command(
            array=commandArray,
            env={
                "XDG_DATA_HOME": CONFIGS,
                "XDG_DATA_DIRS": "/userdata/roms/rott",
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )
