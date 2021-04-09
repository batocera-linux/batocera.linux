#!/usr/bin/env python

from generators.Generator import Generator
import Command

class ShGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        launchfile = rom + "/launch.sh"
        commandArray = ["/bin/sh", launchfile]
        return Command.Command(array=commandArray)

    def getMouseMode(self, config):
        return True
