#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
import batoceraFiles
import codecs
import os

class CGeniusGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        # basis
        commandArray = ["cgenius"]

        # rom
        commandArray.append(rom)

        return Command.Command(array=commandArray)
