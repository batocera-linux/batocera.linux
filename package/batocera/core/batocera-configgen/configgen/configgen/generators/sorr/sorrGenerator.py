#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig


class SorrGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        commandArray = ["bgdi", "-i", "/userdata/roms/sorr", rom]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
