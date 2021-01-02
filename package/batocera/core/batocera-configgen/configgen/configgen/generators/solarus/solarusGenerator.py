#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig


class SolarusGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        commandArray = ["solarus-run", "-fullscreen=yes", "-cursor-visible=no", "-lua-console=no", rom]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
