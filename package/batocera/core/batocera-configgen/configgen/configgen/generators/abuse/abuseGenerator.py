#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig


class AbuseGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        commandArray = ["abuse", "-datadir", "/userdata/roms/abuse/abuse_data"]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
