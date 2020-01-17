#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import os.path
import glob


class ViceGenerator(Generator):

    def getResolutionMode(self, config):
        return 'default'
    
    # Main entry of the module
    # Return command
    def generate(self, system, rom, playersControllers, gameResolution):

        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']] + system.config['core'], 
                        "-config", batoceraFiles.viceConfig, "-autostart", rom]

        return Command.Command(array=commandArray)
