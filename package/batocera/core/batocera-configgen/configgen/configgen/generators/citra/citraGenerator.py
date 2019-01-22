#!/usr/bin/env python
import Command
import recalboxFiles
from generators.Generator import Generator
import shutil
import os.path


class CitraGenerator(Generator):

    # Main entry of the module
    def generate(self, system, rom, playersControllers, gameResolution):
        
        commandArray = [recalboxFiles.recalboxBins[system.config['emulator']], "-f", rom]
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":recalboxFiles.CONF})