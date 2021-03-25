#!/usr/bin/env python

from generators.Generator import Generator
import Command

class FlatpakGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        romId = None
        with open(rom) as f:
            romId = str.strip(f.read())

        commandArray = ["flatpak", "run", romId]
        return Command.Command(array=commandArray)

    def getMouseMode(self, config):
        return True
