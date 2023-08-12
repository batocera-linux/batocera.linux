#!/usr/bin/env python

import os
import configparser
import Command
from generators.Generator import Generator
import batoceraFiles

vpinballConfigPath = batoceraFiles.CONF + "/vpinball"
vpinballConfigFile = vpinballConfigPath + "/VPinballX.ini"
vpinballMusicPath = vpinballConfigPath + "/music"

class VPinballGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        
        # create vpinball config directory
        if not os.path.exists(vpinballConfigPath):
            os.makedirs(vpinballConfigPath)
        # create vpinball music directory
        if not os.path.exists(vpinballMusicPath):
            os.makedirs(vpinballMusicPath)
        
        config = configparser.ConfigParser()

        # ensure we set disableesc=1 to allow graceful shitdown
        if not os.path.exists(vpinballConfigFile):    
            config["Player"] = {"disableesc": "1"}    
        else:
            config.read(vpinballConfigFile)
            if not config.has_section("Player"):
                config["Player"] = {"disableesc": "1"}
            else:
                config["Player"]["disableesc"] = "1"
        
        with open(vpinballConfigFile, "w") as f:
                config.write(f)
        
        # set the config path to be sure
        commandArray = [
            "/usr/bin/vpinball/VPinballX_GL",
            "-PrefPath", vpinballConfigPath,
            "-Play", rom
        ]
        
        return Command.Command(array=commandArray)

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
