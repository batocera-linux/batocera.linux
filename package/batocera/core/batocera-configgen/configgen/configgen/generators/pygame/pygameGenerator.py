#!/usr/bin/env python

import Command
from generators.Generator import Generator
import os

class PygameGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
        commandArray = ["pygame", rom]
        return Command.Command(array=commandArray)

    def executionDirectory(self, config, rom):
        return os.path.dirname(rom)

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
