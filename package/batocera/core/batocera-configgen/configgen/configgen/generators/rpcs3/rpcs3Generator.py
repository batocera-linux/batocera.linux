#!/usr/bin/env python

from generators.Generator import Generator
import batoceraFiles
import Command
import shutil
import os
from utils.logger import eslog
from os import path
from os import environ
import ConfigParser

class Rpcs3Generator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
    
        #Taking care of the CurrentSettings.ini file
        if not os.path.exists(os.path.dirname(batoceraFiles.rpcs3CurrentConfig)):
            os.makedirs(os.path.dirname(batoceraFiles.rpcs3CurrentConfig))

        # Generates CurrentSettings.ini with values to disable prompts on first run
        
        rpcsCurrentSettings = ConfigParser.ConfigParser()
        # To prevent ConfigParser from converting to lower case
        rpcsCurrentSettings.optionxform = str
        if os.path.exists(batoceraFiles.rpcs3CurrentConfig):
            rpcsCurrentSettings.read(batoceraFiles.rpcs3CurrentConfig)
        
        #Sets Gui Settings to close completely and disables some popups
        if not rpcsCurrentSettings.has_section("main_window"):
            rpcsCurrentSettings.add_section("main_window")  
        
        rpcsCurrentSettings.set("main_window", "confirmationBoxExitGame", "false")
        rpcsCurrentSettings.set("main_window", "infoBoxEnabledInstallPUP","false")
        rpcsCurrentSettings.set("main_window", "infoBoxEnabledWelcome","false")
                
        with open(batoceraFiles.rpcs3CurrentConfig, 'w') as configfile:
            rpcsCurrentSettings.write(configfile)
            
        romBasename = path.basename(rom)
        romName = rom + '/PS3_GAME/USRDIR/EBOOT.BIN'
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']],romName]
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_CACHE_HOME":batoceraFiles.SAVES, "QT_QPA_PLATFORM":"xcb"})