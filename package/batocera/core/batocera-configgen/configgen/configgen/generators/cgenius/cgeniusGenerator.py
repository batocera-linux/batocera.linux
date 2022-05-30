#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
import batoceraFiles
import codecs
import os

class CGeniusGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):

        # basis
        commandArray = ["CGeniusExe"]

        # rom
        commandArray.append(rom)

        return Command.Command(array=commandArray)
