#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os

class YuzuGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        #commandArray = ["/usr/bin/yuzu", "-f", "-g", rom ]
        return Command.Command(array=commandArray)
