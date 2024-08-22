#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import configparser
import os
from . import mupenConfig
from . import mupenControllers

class MupenGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # Read the configuration file
        iniConfig = configparser.ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        iniConfig.optionxform = str
        if os.path.exists(batoceraFiles.mupenCustom):
            iniConfig.read(batoceraFiles.mupenCustom)
        else:
            if not os.path.exists(os.path.dirname(batoceraFiles.mupenCustom)):
                os.makedirs(os.path.dirname(batoceraFiles.mupenCustom))
            iniConfig.read(batoceraFiles.mupenCustom)

        mupenConfig.setMupenConfig(iniConfig, system, playersControllers, gameResolution)
        mupenControllers.setControllersConfig(iniConfig, playersControllers, system, wheels)

        # state_slot option, AutoStateSlotIncrement could be set too depending on the es option
        if system.isOptSet('state_slot'):
            iniConfig.set("Core", "CurrentStateSlot", str(system.config["state_slot"]))

        # Save the ini file
        if not os.path.exists(os.path.dirname(batoceraFiles.mupenCustom)):
            os.makedirs(os.path.dirname(batoceraFiles.mupenCustom))
        with open(batoceraFiles.mupenCustom, 'w') as configfile:
            iniConfig.write(configfile)

        # Command
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "--corelib", "/usr/lib/libmupen64plus.so.2.0.0", "--gfx", "/usr/lib/mupen64plus/mupen64plus-video-{}.so".format(system.config['core']), "--configdir", batoceraFiles.mupenConf, "--datadir", batoceraFiles.mupenConf]

        # state_filename option
        if system.isOptSet('state_filename'):
            commandArray.extend(["--savestate", system.config['state_filename']])

        commandArray.append(rom)

        return Command.Command(array=commandArray)

    def getInGameRatio(self, config, gameResolution, rom):
        if ("mupen64plus_ratio" in config and config["mupen64plus_ratio"] == "16/9") or ("mupen64plus_ratio" not in config and "ratio" in config and config["ratio"] == "16/9"):
            return 16/9
        return 4/3
