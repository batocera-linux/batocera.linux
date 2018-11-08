#!/usr/bin/env python
import Command
import recalboxFiles
from generators.Generator import Generator
import os.path
import glob


class ViceGenerator(Generator):

    def getResolutionMode(self, config):
        return 'default'
    
    # Main entry of the module
    # Return command
    def generate(self, system, rom, playersControllers, gameResolution):
        # Settings recalbox default config file if no user defined one
        if not system.config['configfile']:
            # Using recalbox config file
            #system.config['configfile'] = recalboxFiles.mupenCustom
            pass
        # Find rom path
        romPath = os.path.dirname(rom)
        romName = os.path.splitext(os.path.basename(rom))[0]

        commandArray = [recalboxFiles.recalboxBins[system.config['emulator']], 
                        "-config", recalboxFiles.viceConfig,
                        "-autostart", rom]
        if 'args' in system.config and system.config['args'] is not None:
            commandArray.extend(system.config['args'])

        return Command.Command(array=commandArray,  env={"SDL_VIDEO_GL_DRIVER": "/usr/lib/libGLESv2.so"})
