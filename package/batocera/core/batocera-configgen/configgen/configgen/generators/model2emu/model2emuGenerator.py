#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
from shutil import copyfile
import os

class Model2EmuGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        commandArray = ["/usr/wine/proton/bin/wine", "/usr/model2emu/EMULATOR.exe"]
        
        # resolution
        commandArray.append("-res={},{}".format(gameResolution["width"], gameResolution["height"]))
        
        # simplify the rom name (strip the directory & extension)
        romname = rom.replace("/userdata/roms/model2/", "")
        smplromname = romname.replace(".zip", "")

        commandArray.extend(["-fullscreen", smplromname])

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
