#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os

class SteamGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
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

    def getMouseMode(self, config):
        return True
