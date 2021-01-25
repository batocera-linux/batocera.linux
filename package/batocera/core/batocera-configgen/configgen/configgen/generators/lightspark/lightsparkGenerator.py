#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig


class LightsparkGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        commandArray = ["lightspark", "-s", "local-with-networking", rom]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
