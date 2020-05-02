#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import openborControllers
import os
import re

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

        core = system.config['core']
        if system.config["core-forced"]:
            return OpenborGenerator.executeCore(system.config['core'], rom)
        # guess the version to run
        return OpenborGenerator.executeCore(OpenborGenerator.guessCore(rom), rom)

    @staticmethod
    def executeCore(core, rom):
        if core == "openbor4432":
            commandArray = ["OpenBOR4432", rom]
        else:
            commandArray = ["OpenBOR", rom]
        return Command.Command(array=commandArray)

    @staticmethod
    def guessCore(rom):
        versionstr = re.search(r'\[.*([0-9]{4})\]+', os.path.basename(rom))
        if versionstr == None:
            return "openbor"
        version = int(versionstr.group(1))

        if version < 6000:
            return "openbor4432"
        return "openbor"
