#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import openborControllers
import os

class OpenborGenerator(Generator):

    # Main entry of the module
    def generate(self, system, rom, playersControllers, gameResolution):
        configDir = batoceraFiles.CONF + '/openbor'
        if not os.path.exists(configDir):
            os.makedirs(configDir)

        savesDir = batoceraFiles.SAVES + '/openbor'
        if not os.path.exists(savesDir):
            os.makedirs(savesDir)

        # controllers
        openborControllers.generateControllerConfig(configDir + "/config.ini", playersControllers)

        commandArray = ["OpenBOR", rom]
        return Command.Command(array=commandArray)
 
