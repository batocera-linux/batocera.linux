#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig


class SolarusGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        commandArray = ["redream", "--gamedir /userdata/roms/dreamcast", "--fullmode", rom]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
