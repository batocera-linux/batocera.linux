#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import os
import re
from settings.unixSettings import UnixSettings
from utils.logger import eslog
from . import openborControllers

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
        eslog.log("core taken is {}".format(core))

        # config file
        configfilename = "config6510.ini"
        if core == "openbor4432":
            configfilename = "config4432.ini"
        elif core == "openbor6330":
            configfilename = "config6330.ini"
        elif core == "openbor6412":
            configfilename = "config6412.ini"
        elif core == "openbor6510":
            configfilename = "config6510.ini"

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

        config.write()

        return OpenborGenerator.executeCore(core, rom)

    @staticmethod
    def executeCore(core, rom):
        if core == "openbor4432":
            commandArray = ["OpenBOR4432", rom]
        elif core == "openbor6330":
            commandArray = ["OpenBOR6330", rom]
        elif core == "openbor6412":
            commandArray = ["OpenBOR6412", rom]
        elif core == "openbor6510":
            commandArray = ["OpenBOR6510", rom]
        else:
            commandArray = ["OpenBOR6510", rom]
        return Command.Command(array=commandArray)

    @staticmethod
    def guessCore(rom):
        versionstr = re.search(r'\[.*([0-9]{4})\]+', os.path.basename(rom))
        if versionstr == None:
            return "openbor6510"
        version = int(versionstr.group(1))

        if version < 6000:
            return "openbor4432"
        if version < 6400:
            return "openbor6330"
        if version < 6500:
            return "openbor6412"
        return "openbor6510"
