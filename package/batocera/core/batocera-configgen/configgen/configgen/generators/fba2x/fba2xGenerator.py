#!/usr/bin/env python

import Command
import fba2xControllers
import batoceraFiles
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
        if os.path.exists(batoceraFiles.fbaCustom):
            with io.open(batoceraFiles.fbaCustom, 'r', encoding='utf_8_sig') as fp:
                iniConfig.readfp(fp)

        fba2xConfig.updateFBAConfig(iniConfig, system)
        fba2xControllers.updateControllersConfig(iniConfig, system, rom, playersControllers)

        # save the ini file
        if not os.path.exists(os.path.dirname(batoceraFiles.fbaCustom)):
            os.makedirs(os.path.dirname(batoceraFiles.fbaCustom))
        with open(batoceraFiles.fbaCustom, 'w') as configfile:
            iniConfig.write(configfile)

        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "--configfile", batoceraFiles.fbaCustom, '--logfile', batoceraFiles.logdir+"/fba2x.log"]
        commandArray.append(rom)
        return Command.Command(array=commandArray)
