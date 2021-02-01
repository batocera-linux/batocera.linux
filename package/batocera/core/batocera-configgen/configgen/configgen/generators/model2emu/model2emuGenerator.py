#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
from shutil import copyfile
import os

class Model2EmuGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        # todo - add some logic before calling if winetricks has already installed these libraries in the bottle
        env WINE=/usr/wine/lutris/bin/wine /usr/wine/winetricks d3dcompiler_42 d3dx9_42
        
        # what version of wine should we be using?
        commandArray = ["/usr/wine/lutris/bin/wine", "/usr/model2emu/EMULATOR.exe"]
        
        # resolution
        commandArray.append("-res={},{}".format(gameResolution["width"], gameResolution["height"]))
        
        # simplify the rom name (strip the directory & extension)
        romname = rom.replace("/userdata/roms/model2/", "")
        smplromname = romname.replace(".zip", "")

        commandArray.extend(["-fullscreen", smplromname])

        return Command.Command(
            array=commandArray,
            env={
                "WINEPREFIX": "/userdata/saves/model2",
                "vblank_mode": "0",
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })

    
