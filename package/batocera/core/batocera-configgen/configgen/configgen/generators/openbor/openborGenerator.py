#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import os
import re
from settings.unixSettings import UnixSettings
from utils.logger import get_logger
from . import openborControllers

eslog = get_logger(__name__)

class OpenborGenerator(Generator):

    # Main entry of the module
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
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
        eslog.debug(f"core taken is {core}")

        # config file
        configfilename = "config7530.ini"
        if core == "openbor4432":
            configfilename = "config4432.ini"
        elif core == "openbor6412":
            configfilename = "config6412.ini"
        elif core == "openbor7142":
            configfilename = "config7142.ini"
        elif core == "openbor7530":
            configfilename = "config7530.ini"

        config = UnixSettings(configDir + "/" + configfilename, separator='')

        # general
        config.save("fullscreen", "1")
        config.save("usegl", "1")
        config.save("usejoy", "1")

        # options
        if system.isOptSet("openbor_ratio"):
            config.save("stretch", system.config["openbor_ratio"])
        else:
            config.save("stretch", "0")

        if system.isOptSet("openbor_filter"):
            config.save("swfilter", system.config["openbor_filter"])
        else:
            config.save("swfilter", "0")
        
        if system.isOptSet("openbor_vsync"):
            config.save("vsync", system.config["openbor_vsync"])
        else:
            config.save("vsync", "1")

        if system.isOptSet("openbor_limit"):
            config.save("fpslimit", system.config["openbor_limit"])
        else:
            config.save("fpslimit", "0")

        # controllers
        openborControllers.generateControllerConfig(config, playersControllers, core)

        # rumble
        if system.isOptSet("openbor_rumble"):
            config.save("joyrumble.0", system.config["openbor_rumble"])
            config.save("joyrumble.1", system.config["openbor_rumble"])
            config.save("joyrumble.2", system.config["openbor_rumble"])
            config.save("joyrumble.3", system.config["openbor_rumble"])
        else:
            config.save("joyrumble.0", "0")
            config.save("joyrumble.1", "0")
            config.save("joyrumble.2", "0")
            config.save("joyrumble.3", "0")

        config.write()

        # change directory for wider compatibility
        os.chdir("/userdata/roms/openbor")

        return OpenborGenerator.executeCore(core, rom)

    @staticmethod
    def executeCore(core, rom):
        if core == "openbor4432":
            commandArray = ["OpenBOR4432", rom]
        elif core == "openbor6412":
            commandArray = ["OpenBOR6412", rom]
        elif core == "openbor7142":
            commandArray = ["OpenBOR7142", rom]
        elif core == "openbor7530":
            commandArray = ["OpenBOR7530", rom]
        else:
            commandArray = ["OpenBOR7530", rom]
        return Command.Command(array=commandArray)

    @staticmethod
    def guessCore(rom):
        versionstr = re.search(r'\[.*([0-9]{4})\]+', os.path.basename(rom))
        if versionstr == None:
            return "openbor7530"
        version = int(versionstr.group(1))

        if version < 6000:
            return "openbor4432"
        if version < 6500:
            return "openbor6412"
        if version < 7530:
            return "openbor7142"
        return "openbor7530"
