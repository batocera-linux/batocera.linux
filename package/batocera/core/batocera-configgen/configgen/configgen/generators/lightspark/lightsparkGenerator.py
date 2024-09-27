from ... import Command
from ..Generator import Generator


class LightsparkGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["lightspark", "-s", "local-with-networking", rom]
        return Command.Command(
            array=commandArray)

    def getMouseMode(self, config, rom):
        return True

    def getHotkeysContext(self):
        return {
            "name": "lightspark",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }
