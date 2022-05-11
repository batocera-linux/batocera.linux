#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import controllersConfig
import os
from os import path

vitaConfig = batoceraFiles.CONF + '/vita'
vitaSaves = batoceraFiles.SAVES + '/vita'
vitaHome = batoceraFiles.CONF

class PlayGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        # Create config folder
        if not path.isdir(vitaConfig):
            os.mkdir(vitaConfig)

        # Create save folder
        if not path.isdir(vitaSaves):
            os.mkdir(vitaSaves)

        commandArray = ["/usr/bin/Vita3K", "-B Vulkan", "-F", "-f", vitaConfig, rom]
        return Command.Command(
            array=commandArray,
            )

    def getMouseMode(self, config):
        return True
