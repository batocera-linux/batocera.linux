#!/usr/bin/env python

import batoceraFiles
from generators.Generator import Generator
import os
import configparser
import io
import Command
from . import fba2xConfig
from . import fba2xControllers

fbaRoot = batoceraFiles.CONF + '/fba/'
fbaCustom = fbaRoot + 'fba2x.cfg'

class Fba2xGenerator(Generator):
    def generate(self, system, rom, playersControllers, guns, gameResolution):
        iniConfig = configparser.ConfigParser()
        # To prevent ConfigParser from converting to lower case
        iniConfig.optionxform = str
        if os.path.exists(fbaCustom):
            iniConfig.read(fbaCustom)

        fba2xConfig.updateFBAConfig(iniConfig, system)
        fba2xControllers.updateControllersConfig(iniConfig, rom, playersControllers)

        # save the ini file
        if not os.path.exists(os.path.dirname(fbaCustom)):
            os.makedirs(os.path.dirname(fbaCustom))
        with open(fbaCustom, 'w') as configfile:
            iniConfig.write(configfile)

        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "--configfile", fbaCustom, '--logfile', batoceraFiles.logdir+"/fba2x.log"]
        commandArray.append(rom)
        return Command.Command(array=commandArray)
