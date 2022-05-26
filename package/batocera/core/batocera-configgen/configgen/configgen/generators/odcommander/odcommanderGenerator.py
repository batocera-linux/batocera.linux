#!/usr/bin/env python

from generators.Generator import Generator
import Command
import controllersConfig

class OdcommanderGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        commandArray = ["od-commander"]

        return Command.Command(array=commandArray,env={
            "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)
        })
