#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig


class VoidswGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        addon = "-addon0"
        if (rom.__contains__("WT")):
            addon = "-addon1"

        if (rom.__contains__("TD")):
            addon = "-addon2"

        commandArray = ["voidsw", addon, "-j/userdata/roms/voidsw"]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
