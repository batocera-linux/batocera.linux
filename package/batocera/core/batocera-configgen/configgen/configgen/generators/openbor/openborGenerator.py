#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import openborControllers
import os
import re
from settings.unixSettings import UnixSettings

class OpenborGenerator(Generator):

    # Main entry of the module
    def generate(self, system, rom, playersControllers, gameResolution):
        configDir = batoceraFiles.CONF + '/openbor'
        if not os.path.exists(configDir):
            os.makedirs(configDir)

        savesDir = batoceraFiles.SAVES + '/openbor'
        if not os.path.exists(savesDir):
            os.makedirs(savesDir)

        # guess the version to run
        core = system.config['core']
        if system.config["core-forced"] == False:
            core = OpenborGenerator.guessCore(rom)

        # config file
        configfilename = "config.ini"
        if core == "openbor4432":
            configfilename = "config4432.ini"

        config = UnixSettings(configDir + "/" + configfilename, separator='')

        # general
        config.save("fullscreen", "1")
        config.save("vsync", "1")
        config.save("usegl", "1")
        config.save("usejoy", "1")

        # options
        if system.isOptSet("ratio"):
            config.save("stretch", system.config["ratio"])
        else:
            config.remove("stretch")

        if system.isOptSet("filter"):
            config.save("swfilter", system.config["filter"])
        else:
            config.remove("swfilter")

        # controllers
        openborControllers.generateControllerConfig(config, playersControllers, core)

        return OpenborGenerator.executeCore(core, rom)

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
