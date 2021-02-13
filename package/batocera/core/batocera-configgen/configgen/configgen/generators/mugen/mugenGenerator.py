#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
import controllersConfig
import re

class MugenGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        # Open config
        settings_path = rom + "/data/mugen.cfg"
        with open(settings_path, 'r') as f:
            contents = f.read()

        # Fix Parser issue
        contents = re.sub(r'.;', ';', contents)
        # Change FullScreen to 1
        contents = re.sub(r'FullScreen\s*=\s*0', 'FullScreen = 1', contents)
        # Change GameWidth to Native resolution
        contents = re.sub(r'GameWidth\s*=\s*[1-9][0-9]*', 'GameWidth = {0}'.format(gameResolution["width"]), contents)
        # Change GameHeight to Native resolution
        contents = re.sub(r'GameHeight\s*=\s*[1-9][0-9]*', 'GameHeight = {0}'.format(gameResolution["height"]), contents)
        
        # Save config
        with open(settings_path, 'w') as f:
            f.write(contents)

        commandArray = ["batocera-wine", "mugen", "play", rom]
        return Command.Command(array=commandArray, env={ "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers) })
