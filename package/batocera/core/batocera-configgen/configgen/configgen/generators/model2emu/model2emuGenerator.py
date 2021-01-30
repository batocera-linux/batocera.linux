#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
from shutil import copyfile
import os

class Model2EmuGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        commandArray = ["/usr/wine/lutris/bin/wine64", "/usr/model2emu/emulator_multicpu.exe", rom]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
