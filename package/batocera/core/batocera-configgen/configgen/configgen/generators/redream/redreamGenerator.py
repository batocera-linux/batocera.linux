#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig


class RedreamGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        commandArray = ["redream", rom]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
                'HOME': "/userdata/system/configs/redream" # to force redream to read/write config file here
            })
