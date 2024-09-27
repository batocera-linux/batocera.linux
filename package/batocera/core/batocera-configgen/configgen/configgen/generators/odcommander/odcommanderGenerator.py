from ... import Command
from ... import controllersConfig
from ..Generator import Generator

class OdcommanderGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["od-commander"]

        return Command.Command(array=commandArray,env={
            "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)
        })

    def getHotkeysContext(self):
        return {
            "name": "odcommander",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }
