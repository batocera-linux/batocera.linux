#!/usr/bin/env python
import Command
#~ import reicastControllers
import batoceraFiles
from generators.Generator import Generator
import shutil
import os.path
import configparser
# TODO: python3 - delete me!
import codecs
from . import ppssppConfig
from . import ppssppControllers

class PPSSPPGenerator(Generator):

    # Main entry of the module
    # Configure fba and return a command
    def generate(self, system, rom, playersControllers, gameResolution):
        ppssppConfig.writePPSSPPConfig(system)
        # For each pad detected
        for index in playersControllers :
            controller = playersControllers[index]
            # we only care about player 1
            if controller.player != "1":
                continue
            ppssppControllers.generateControllerConfig(controller)
            # TODO: python 3 - workawround to encode files in utf-8
            cfgFile = codecs.open(batoceraFiles.ppssppControls, "w", "utf-8")
            cfgFile.write(controller.generateSDLGameDBLine())
            cfgFile.close()
            break

        # the command to run
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']]]
        commandArray.append(rom)
        commandArray.append("--fullscreen")

        # adapt the menu size
        if PPSSPPGenerator.isLowResolution(gameResolution):
            commandArray.extend(["--dpi", "0.5"])

        # The next line is a reminder on how to quit PPSSPP with just the HK
        #commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], rom, "--escape-exit"]
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF, "QT_QPA_PLATFORM":"xcb", "PPSSPP_GAME_CONTROLLER_DB_PATH": batoceraFiles.ppssppControls})

    @staticmethod
    def isLowResolution(gameResolution):
        return gameResolution["width"] < 400 or gameResolution["height"] < 400
