#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig


class EasyRPGGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        commandArray = ["easyrpg-player", rom]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
