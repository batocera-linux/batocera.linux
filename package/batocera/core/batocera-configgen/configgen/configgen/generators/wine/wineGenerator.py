#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
from os import path

class WineGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        romBasename = path.basename(rom)

        if system.name == "windows_installers":
            commandArray = ["batocera-wine", "install", romBasename]
            return Command.Command(array=commandArray)
        else:
            commandArray = ["batocera-wine", "play", romBasename]
            return Command.Command(array=commandArray)
