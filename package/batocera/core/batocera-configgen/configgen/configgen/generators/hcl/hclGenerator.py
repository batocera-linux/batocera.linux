#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig


class HclGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        commandArray = ["hcl"]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
