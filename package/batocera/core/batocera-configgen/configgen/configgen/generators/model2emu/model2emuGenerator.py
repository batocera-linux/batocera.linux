#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
from shutil import copyfile
import os

class Model2EmuGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        #configdir = "/userdata/system/configs/model2emu"
        #if not os.path.exists(configdir):
        #    os.makedirs(configdir)

        #copyfile("/usr/bin/model2emu/EMULATOR.INI", configdir + "/EMULATOR.INI")
        #os.chmod(configdir + "/EMULATOR.INI", 0775)

        commandArray = ["/usr/wine/lutris/bin/wine64", "/usr/model2emu/emulator_multicpu.exe", rom]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
