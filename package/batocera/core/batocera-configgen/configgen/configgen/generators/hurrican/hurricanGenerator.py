#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
import os

class HurricanGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        os.chdir("/usr/share/hurrican")
        commandArray = ["hurrican"]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
