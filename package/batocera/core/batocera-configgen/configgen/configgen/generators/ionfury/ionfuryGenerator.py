#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig


class IonfuryGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        commandArray = ["ionfury", "-game_dir", "/userdata/roms/ionfury", "-g", rom]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
