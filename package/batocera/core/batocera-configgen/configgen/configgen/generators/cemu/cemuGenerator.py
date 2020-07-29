#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
from os import path

class CemuGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        romBasename = path.basename(rom)

        commandArray = ["batocera-wine", "/usr/bin/cemu/Cemu.exe", romBasename]
        return Command.Command(array=commandArray)
