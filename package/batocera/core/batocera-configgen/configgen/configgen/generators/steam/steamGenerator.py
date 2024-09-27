import os

from ... import Command
from ..Generator import Generator

class SteamGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        basename = os.path.basename(rom)
        gameId = None
        if basename != "Steam.steam":
            # read the id inside the file
            with open(rom) as f:
                gameId = str.strip(f.read())

        if gameId is None:
            commandArray = ["batocera-steam"]
        else:
            commandArray = ["batocera-steam", gameId]
        return Command.Command(array=commandArray)

    def getMouseMode(self, config, rom):
        return True

    def getHotkeysContext(self):
        return {
            "name": "steam",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }
