#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
import os

class OpenJazzGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
        try:
            os.chdir("/userdata/roms/openjazz/")
        except:
            eslog.error("ERROR: Game assets not installed. You can get them from the Batocera Content Downloader.")
        commandArray = ["OpenJazz"]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
