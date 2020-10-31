#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
from os import path

class WineGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        if system.name == "windows_installers":
            commandArray = ["batocera-wine", "install", rom]
            return Command.Command(array=commandArray)
        elif system.name == "windows":
            commandArray = ["batocera-wine", "play", rom]
            return Command.Command(array=commandArray)

        raise Exception("invalid system " + system.name)
