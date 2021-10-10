#!/usr/bin/env python

import batoceraFiles
from generators.Generator import Generator
import os
import configparser
import io
import Command
from . import fba2xConfig
from . import fba2xControllers

class Fba2xGenerator(Generator):
    def generate(self, system, rom, playersControllers, gameResolution):
        iniConfig = configparser.ConfigParser()
        # To prevent ConfigParser from converting to lower case
        iniConfig.optionxform = str
        if os.path.exists(batoceraFiles.fbaCustom):
            with io.open(batoceraFiles.fbaCustom, 'r', encoding='utf_8_sig') as fp:
                iniConfig.readfp(fp)

        fba2xConfig.updateFBAConfig(iniConfig, system)
        fba2xControllers.updateControllersConfig(iniConfig, rom, playersControllers)

        # save the ini file
        if not os.path.exists(os.path.dirname(batoceraFiles.fbaCustom)):
            os.makedirs(os.path.dirname(batoceraFiles.fbaCustom))
        with open(batoceraFiles.fbaCustom, 'w') as configfile:
            iniConfig.write(configfile)

        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "--configfile", batoceraFiles.fbaCustom, '--logfile', batoceraFiles.logdir+"/fba2x.log"]
        commandArray.append(rom)
        return Command.Command(array=commandArray)
