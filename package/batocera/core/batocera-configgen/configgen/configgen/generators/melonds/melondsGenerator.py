#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
from os import path

class MelonDSGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        romBasename = path.basename(rom)

        commandArray = ["/usr/bin/melonDS", rom]
        return Command.Command(array=commandArray)
