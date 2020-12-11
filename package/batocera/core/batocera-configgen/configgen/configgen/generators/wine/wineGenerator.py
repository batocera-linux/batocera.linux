#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
from os import path
import controllersConfig

class WineGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        if system.name == "windows_installers":
            commandArray = ["batocera-wine", "install", rom]
            return Command.Command(array=commandArray)
        elif system.name == "windows":
            commandArray = ["batocera-wine", "play", rom]
            return Command.Command(array=commandArray,env={
                "vblank_mode": "0",
                "mesa_glthread": "true",
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers),
                "__GL_THREADED_OPTIMIZATIONS": "1"
            })

        raise Exception("invalid system " + system.name)
