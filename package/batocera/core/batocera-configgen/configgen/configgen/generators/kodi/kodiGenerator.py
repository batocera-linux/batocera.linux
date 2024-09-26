from ... import batoceraFiles
from ... import Command
from ..Generator import Generator
from . import kodiConfig

class KodiGenerator(Generator):

    # Main entry of the module
    # Configure kodi inputs and return the command to run
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        kodiConfig.writeKodiConfig(playersControllers)
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']]]
        return Command.Command(array=commandArray)

    def getHotkeysContext(self):
        return {
            "name": "kodi",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }
