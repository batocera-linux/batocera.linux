#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig


class LightsparkGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        commandArray = ["lightspark", "-s", "local-with-networking", rom]
        return Command.Command(
            array=commandArray)

    def getMouseMode(self, config):
        return True
