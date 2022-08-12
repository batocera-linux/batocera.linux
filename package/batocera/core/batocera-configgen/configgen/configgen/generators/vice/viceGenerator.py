#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import os.path
import glob
from . import viceConfig
from . import viceControllers

class ViceGenerator(Generator):

    def getResolutionMode(self, config):
        return 'default'
    
    # Main entry of the module
    # Return command
    def generate(self, system, rom, playersControllers, guns, gameResolution):

        if not os.path.exists(os.path.dirname(batoceraFiles.viceConfig)):
            os.makedirs(os.path.dirname(batoceraFiles.viceConfig))

        # configuration file
        viceConfig.setViceConfig(batoceraFiles.viceConfig, system, guns, rom)

        # controller configuration
        viceControllers.generateControllerConfig(batoceraFiles.viceConfig, playersControllers)

        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']] + system.config['core'], "-autostart", rom]

        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF})
