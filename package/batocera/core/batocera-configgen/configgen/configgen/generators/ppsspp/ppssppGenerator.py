#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import shutil
import os
import configparser
import controllersConfig
from . import ppssppConfig
from . import ppssppControllers

class PPSSPPGenerator(Generator):

    # Main entry of the module
    # Configure fba and return a command
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        ppssppConfig.writePPSSPPConfig(system)

        # Remove the old gamecontrollerdb.txt file
        dbpath = "/userdata/system/configs/ppsspp/gamecontrollerdb.txt"
        if os.path.exists(dbpath):
            os.remove(dbpath)
        
        # Generate the controls.ini
        for index in playersControllers :
            controller = playersControllers[index]
            # We only care about player 1
            if controller.player != "1":
                continue
            ppssppControllers.generateControllerConfig(controller)
            break

        # The command to run
        commandArray = ['/usr/bin/PPSSPP']
        commandArray.append(rom)
        commandArray.append("--fullscreen")

        # Adapt the menu size to low defenition
        # I've played with this option on PC to fix menu size in Hi-Resolution and it not working fine. I'm almost sure this option break the emulator (Darknior)
        if PPSSPPGenerator.isLowResolution(gameResolution):
            commandArray.extend(["--dpi", "0.5"])

        # state_slot option
        if system.isOptSet('state_filename'):
            commandArray.append("--state={}".format(system.config['state_filename']))

        # The next line is a reminder on how to quit PPSSPP with just the HK
        #commandArray = ['/usr/bin/PPSSPP'], rom, "--escape-exit"]

        # select the correct pad
        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            if nplayer == 1:
                commandArray.extend(["--njoy", str(pad.index)])
            nplayer = nplayer +1

        return Command.Command(
            array=commandArray, 
            env={
                "XDG_CONFIG_HOME":batoceraFiles.CONF,
                "XDG_DATA_HOME":batoceraFiles.SAVES,
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)
            }
        )
    
    @staticmethod
    def isLowResolution(gameResolution):
        return gameResolution["width"] <= 480 or gameResolution["height"] <= 480

    # Show mouse on screen for the Config Screen
    def getMouseMode(self, config, rom):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
