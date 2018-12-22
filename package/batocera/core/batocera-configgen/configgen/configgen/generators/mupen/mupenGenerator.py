#!/usr/bin/env python
import Command
import mupenConfig
import mupenControllers
import recalboxFiles
from generators.Generator import Generator


class MupenGenerator(Generator):

    # Main entry of the module
    # Configure mupen and return a command
    def generate(self, system, rom, playersControllers, gameResolution):
        # Settings recalbox default config file if no user defined one
        if not 'configfile' in system.config:
            # Using recalbox config file
            system.config['configfile'] = recalboxFiles.mupenCustom
            # Write configuration file
            mupenConfig.writeMupenConfig(system, playersControllers, gameResolution)
            #  Write controllers configuration files
            mupenControllers.writeControllersConfig(playersControllers)

        commandArray = [recalboxFiles.recalboxBins[system.config['emulator']], "--corelib", "/usr/lib/libmupen64plus.so.2.0.0", "--gfx", "/usr/lib/mupen64plus/mupen64plus-video-{}.so".format(system.config['core']),
                        "--configdir", recalboxFiles.mupenConf, "--datadir", recalboxFiles.mupenConf]
        commandArray.append(rom)

        return Command.Command(array=commandArray, env={"SDL_VIDEO_GL_DRIVER":"/usr/lib/libGLESv2.so"})
