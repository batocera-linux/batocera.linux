#!/usr/bin/env python

from generators.Generator import Generator
import Command

class FlatpakGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        romId = None
        with open(rom) as f:
            romId = str.strip(f.read())

        # the directory monitor must exist and all the dirs must be owned by batocera
        commandArray = ["su", "batocera", "-c",  "flatpak run " + romId]
        return Command.Command(array=commandArray)

    def getMouseMode(self, config):
        return True
