#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import supermodel3Controllers
import os
import re
from settings.unixSettings import UnixSettings
from utils.logger import eslog

class Supermodel3Generator(Generator):

    # Main entry of the module
    def generate(self, system, rom, playersControllers, gameResolution):
        launchDir = batoceraFiles.supermodel3Custom
        #os.makedirs(launchDir)
        eslog.log(system.config["core"])
        eslog.log(launchDir)
        
        # Saves, Snaps, NVRAM dir
        
        # controllers
        #config = UnixSettings(batoceraFiles.supermodel3Config + "/" + 'testControls.ini', separator='')
        supermodel3Controllers.generateControllerConfig(batoceraFiles.supermodel3Ini, playersControllers)

        #commandArray = [batoceraFiles.batoceraBins[core], rom, '-fullscreen', '-res=1920,1080' '-game-xml-file='+launchDir+'/Games.xml']
        commandArray = [batoceraFiles.batoceraBins[system.config["core"]], rom, '-fullscreen', '-res=1920,1080']
        os.chdir(launchDir)        
        return Command.Command(array=commandArray) 
        
            
