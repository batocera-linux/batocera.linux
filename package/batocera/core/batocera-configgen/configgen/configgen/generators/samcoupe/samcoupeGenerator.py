from ... import Command
from ... import controllersConfig
from ..Generator import Generator


class SamcoupeGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["simcoupe", "autoboot", "-disk1", rom]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })

    def getHotkeysContext(self):
        return {
            "name": "samcoupe",
            "keys": { "exit": ["KEY_LEFTCTRL", "KEY_F12"], "menu": "KEY_F10" }
        }
