#!/usr/bin/env python
import Command
from . import mupenConfig
from . import mupenControllers
import batoceraFiles
from generators.Generator import Generator
import configparser
import os

class MupenGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        # read the configuration file
        iniConfig = configparser.ConfigParser()
        # To prevent ConfigParser from converting to lower case
        iniConfig.optionxform = str
        if os.path.exists(batoceraFiles.mupenCustom):
            iniConfig.read(batoceraFiles.mupenCustom)

        mupenConfig.setMupenConfig(iniConfig, system, playersControllers, gameResolution)
        mupenControllers.setControllersConfig(iniConfig, playersControllers, system.config)

        # save the ini file
        if not os.path.exists(os.path.dirname(batoceraFiles.mupenCustom)):
            os.makedirs(os.path.dirname(batoceraFiles.mupenCustom))
        with open(batoceraFiles.mupenCustom, 'w') as configfile:
            iniConfig.write(configfile)

        # command
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "--corelib", "/usr/lib/libmupen64plus.so.2.0.0", "--gfx", "/usr/lib/mupen64plus/mupen64plus-video-{}.so".format(system.config['core']), "--configdir", batoceraFiles.mupenConf, "--datadir", batoceraFiles.mupenConf]
        commandArray.append(rom)

        return Command.Command(array=commandArray)
