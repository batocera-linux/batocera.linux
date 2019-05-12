#!/usr/bin/env python
import Command
#~ import reicastControllers
import batoceraFiles
from generators.Generator import Generator
import ppssppConfig
import ppssppControllers
import shutil
import os.path
import ConfigParser
# TODO: python3 - delete me!
import codecs

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
        # The next line is a reminder on how to quit PPSSPP with just the HK
        #commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], rom, "--escape-exit"]
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF, "SDL_VIDEO_GL_DRIVER": "/usr/lib/libGLESv2.so", "SDL_VIDEO_EGL_DRIVER": "/usr/lib/libGLESv2.so", "PPSSPP_GAME_CONTROLLER_DB_PATH": batoceraFiles.ppssppControls})
