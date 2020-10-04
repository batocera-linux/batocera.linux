#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
from os import path

class WineGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        romBasename = path.basename(rom)

        if system.name == "windows32_installers":
            commandArray = ["batocera-wine", "install", 32, romBasename]
            return Command.Command(array=commandArray)
        elif system.name == "windows32":
            commandArray = ["batocera-wine", "play", 32, romBasename]
            return Command.Command(array=commandArray)
        elif system.name == "windows64_installers":
            commandArray = ["batocera-wine", "install", 64, romBasename]
            return Command.Command(array=commandArray)
        elif system.name == "windows64":
            commandArray = ["batocera-wine", "play", 64, romBasename]
            return Command.Command(array=commandArray)
