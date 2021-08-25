#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import controllersConfig
import os
from os import path

class PlayGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        commandArray = ["play", "--disc", rom]
        return Command.Command(
            array=commandArray)

    def getMouseMode(self, config):
        return True
