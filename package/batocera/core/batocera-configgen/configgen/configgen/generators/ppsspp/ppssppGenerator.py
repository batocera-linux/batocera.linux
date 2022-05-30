#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import shutil
import os.path
import configparser
# TODO: python3 - delete me!
import codecs
from . import ppssppConfig
from . import ppssppControllers

ppssppControls = batoceraFiles.CONF + '/ppsspp/gamecontrollerdb.txt'


class PPSSPPGenerator(Generator):

    # Main entry of the module
    # Configure fba and return a command
    def generate(self, system, rom, playersControllers, guns, gameResolution):
        ppssppConfig.writePPSSPPConfig(system)
        # For each pad detected
        for index in playersControllers :
            controller = playersControllers[index]
            # We only care about player 1
            if controller.player != "1":
                continue
            ppssppControllers.generateControllerConfig(controller)
            # TODO: python 3 - workawround to encode files in utf-8
            cfgFile = codecs.open(ppssppControls, "w", "utf-8")
            cfgFile.write(controller.generateSDLGameDBLine())
            cfgFile.close()
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
            commandArray.extend(["--state", "/userdata/saves/psp/{}".format(system.config['state_filename'])])

        # The next line is a reminder on how to quit PPSSPP with just the HK
        #commandArray = ['/usr/bin/PPSSPP'], rom, "--escape-exit"]
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_RUNTIME_DIR":batoceraFiles.HOME_INIT, "PPSSPP_GAME_CONTROLLER_DB_PATH": ppssppControls})

    @staticmethod
    def isLowResolution(gameResolution):
        return gameResolution["width"] <= 480 or gameResolution["height"] <= 480

    # Show mouse on screen for the Config Screen
    def getMouseMode(self, config):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
