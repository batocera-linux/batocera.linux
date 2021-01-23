#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
from os import path
import controllersConfig

class MugenGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        if system.name == "mugen":
            commandArray = ["batocera-wine", "mugen", "play", rom]
            return Command.Command(array=commandArray,env={
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers),
            })

        config = UnixSettings(rom + "/data + mugen.cfg, separator='')

        # general
        config.save("FullScreen", "1")
        config.save("GameWidth", "1920")
        config.save("GameHeight", "1080")
        config.save("Language", "en")

        raise Exception("invalid system " + system.name)
