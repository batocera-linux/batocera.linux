#!/usr/bin/env python
import Command
#~ import reicastControllers
import recalboxFiles
from generators.Generator import Generator
import ppssppConfig
import ppssppControllers
import shutil
import os.path
import ConfigParser


class PPSSPPGenerator(Generator):

    # Main entry of the module
    # Configure fba and return a command
    def generate(self, system, rom, playersControllers, gameResolution):
        if not system.config['configfile']:
            ppssppConfig.writePPSSPPConfig(system)
            # For each pad detected
            for index in playersControllers :
                controller = playersControllers[index]
                # we only care about player 1
                if controller.player != "1":
                    continue
                ppssppControllers.generateControllerConfig(controller)
                cfgFile = open(recalboxFiles.ppssppControls, "w")
                cfgFile.write(controller.generateSDLGameDBLine())
                cfgFile.close()
                break

        # the command to run  
        commandArray = [recalboxFiles.recalboxBins[system.config['emulator']]]
        if 'args' in system.config and system.config['args'] is not None:
            commandArray.extend(system.config['args'])
        commandArray.append(rom)
        # The next line is a reminder on how to quit PPSSPP with just the HK
        #commandArray = [recalboxFiles.recalboxBins[system.config['emulator']], rom, "--escape-exit"]
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":recalboxFiles.CONF, "SDL_VIDEO_GL_DRIVER": "/usr/lib/libGLESv2.so", "SDL_VIDEO_EGL_DRIVER": "/usr/lib/libGLESv2.so", "PPSSPP_GAME_CONTROLLER_DB_PATH": recalboxFiles.ppssppControls})
