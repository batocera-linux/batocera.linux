#!/usr/bin/env python
import Command
import mupenConfig
import mupenControllers
import recalboxFiles
from generators.Generator import Generator
import ConfigParser
import os

class MupenGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        # read the configuration file
        iniConfig = ConfigParser.ConfigParser()
        # To prevent ConfigParser from converting to lower case
        iniConfig.optionxform = str
        if os.path.exists(recalboxFiles.mupenCustom):
            iniConfig.read(recalboxFiles.mupenCustom)

        mupenConfig.setMupenConfig(iniConfig, system, playersControllers, gameResolution)
        mupenControllers.setControllersConfig(iniConfig, playersControllers)

        # save the ini file
        if not os.path.exists(os.path.dirname(recalboxFiles.mupenCustom)):
            os.makedirs(os.path.dirname(recalboxFiles.mupenCustom))
        with open(recalboxFiles.mupenCustom, 'w') as configfile:
            iniConfig.write(configfile)

        # command
        commandArray = [recalboxFiles.recalboxBins[system.config['emulator']], "--corelib", "/usr/lib/libmupen64plus.so.2.0.0", "--gfx", "/usr/lib/mupen64plus/mupen64plus-video-{}.so".format(system.config['core']), "--configdir", recalboxFiles.mupenConf, "--datadir", recalboxFiles.mupenConf]
        commandArray.append(rom)

        return Command.Command(array=commandArray, env={"SDL_VIDEO_GL_DRIVER":"/usr/lib/libGLESv2.so"})
