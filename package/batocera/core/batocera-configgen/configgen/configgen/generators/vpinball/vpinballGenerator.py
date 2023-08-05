#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
import batoceraFiles
import os

vpinballConfig = batoceraFiles.CONF + "/vpinball"

class VPinballGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        
        # create vpinball config directory
        if not os.path.exists(vpinballConfig):
            os.makedirs(vpinballConfig)
        
        commandArray = ["/usr/bin/vpinball/VPinballX_GL", "-PrefPath", vpinballConfig, "-Play", rom]
        
        return Command.Command(array=commandArray)

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
