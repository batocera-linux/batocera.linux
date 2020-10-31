#!/usr/bin/env python

import Command
from generators.Generator import Generator

class PygameGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        commandArray = ["batocera-pygame", rom]
        return Command.Command(array=commandArray)
