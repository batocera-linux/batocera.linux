#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import kodiConfig

class KodiGenerator(Generator):
    
    # Main entry of the module
    # Configure kodi inputs and return the command to run
    def generate(self, system, rom, playersControllers, gameResolution):
        kodiConfig.writeKodiConfig(playersControllers)
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']]]
        return Command.Command(array=commandArray)
