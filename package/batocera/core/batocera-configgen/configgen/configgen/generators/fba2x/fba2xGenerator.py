#!/usr/bin/env python

import Command
import fba2xControllers
import recalboxFiles
import fba2xConfig
from generators.Generator import Generator
import os.path
import ConfigParser
import io

class Fba2xGenerator(Generator):
    def generate(self, system, rom, playersControllers, gameResolution):
        iniConfig = ConfigParser.ConfigParser()
        # To prevent ConfigParser from converting to lower case
        iniConfig.optionxform = str
        if os.path.exists(recalboxFiles.fbaCustom):
            with io.open(recalboxFiles.fbaCustom, 'r', encoding='utf_8_sig') as fp:
                iniConfig.readfp(fp)

        fba2xConfig.updateFBAConfig(iniConfig, system)
        fba2xControllers.updateControllersConfig(iniConfig, system, rom, playersControllers)

        # save the ini file
        if not os.path.exists(os.path.dirname(recalboxFiles.fbaCustom)):
            os.makedirs(os.path.dirname(recalboxFiles.fbaCustom))
        with open(recalboxFiles.fbaCustom, 'w') as configfile:
            iniConfig.write(configfile)

        commandArray = [recalboxFiles.recalboxBins[system.config['emulator']], "--configfile", recalboxFiles.fbaCustom, '--logfile', recalboxFiles.logdir+"/fba2x.log"]
        commandArray.append(rom)
        return Command.Command(array=commandArray)
