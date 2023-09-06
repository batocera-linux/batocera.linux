#!/usr/bin/env python

import os
import configparser
import Command
from generators.Generator import Generator
import batoceraFiles

vpinballConfigPath = batoceraFiles.CONF + "/vpinball"
vpinballMusicPath = vpinballConfigPath + "/music"

class VPinballGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
        
        # create vpinball config directory
        if not os.path.exists(vpinballConfigPath):
            os.makedirs(vpinballConfigPath)
        # create vpinball music directory
        if not os.path.exists(vpinballMusicPath):
            os.makedirs(vpinballMusicPath)
        
        # set the config path to be sure
        commandArray = [
            "/usr/bin/vpinball/VPinballX_GL",
            "-PrefPath", vpinballConfigPath,
            "-Play", rom
        ]
        
        return Command.Command(array=commandArray)

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
