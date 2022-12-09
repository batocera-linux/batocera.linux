#!/usr/bin/env python
from generators.Generator import Generator
import Command
import os
import controllersConfig
import re

class MugenGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):

        settings_path = rom + "/data/mugen.cfg"
        with open(settings_path, 'r', encoding='utf-8-sig') as f:
            contents = f.read()

        #clean up
        contents = re.sub(r'^[ ]*;', ';', contents, 0, re.MULTILINE)
        contents = re.sub(r'^[ ;]*FullScreen[ ]*=.*', 'FullScreen = 1', contents, 0, re.MULTILINE)
        contents = re.sub(r'^[ ;]*GameWidth[ ]*=.*', 'Width = '+str(gameResolution["width"]), contents, 0, re.MULTILINE)
        contents = re.sub(r'^[ ;]*GameHeight[ ]*=.*', 'Height = '+str(gameResolution["height"]), contents, 0, re.MULTILINE)
        contents = re.sub(r'^[ ;]*Width[ ]*=.*', 'GameWidth = '+str(gameResolution["width"]), contents, 0, re.MULTILINE)
        contents = re.sub(r'^[ ;]*Height[ ]*=.*', 'GameHeight = '+str(gameResolution["height"]), contents, 0, re.MULTILINE)
        contents = re.sub(r'^[ ;]*Language[ ]*=.*', 'Language = "en"', contents, 0, re.MULTILINE)
        with open(settings_path, 'w') as f:
            f.write(contents)

        # Save config
        if not os.path.exists(os.path.dirname(settings_path)):
            os.makedirs(os.path.dirname(settings_path))

        commandArray = ["batocera-wine", "mugen", "play", rom]
        return Command.Command(array=commandArray, env={ "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers) })
