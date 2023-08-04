#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
import os

class HclGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        os.chdir("/usr/share/hcl")
        commandArray = ["hcl"]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
