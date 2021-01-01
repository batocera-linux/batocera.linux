#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig


class HatariGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        commandArray = ["hatari", "--fullscreen" ]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
