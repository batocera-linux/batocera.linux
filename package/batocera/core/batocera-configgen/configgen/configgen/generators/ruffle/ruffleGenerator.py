#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig


class RuffleGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
        commandArray = ["ruffle", rom]
        return Command.Command(
            array=commandArray)

    def getMouseMode(self, config):
        return True
