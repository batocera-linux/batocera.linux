#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig


class SamcoupeGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        commandArray = ["simcoupe", "autoboot", "-disk1", rom]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
