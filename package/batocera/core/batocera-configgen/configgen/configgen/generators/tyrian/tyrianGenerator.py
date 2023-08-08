#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
import os

class TyrianGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        try:
            os.chdir("/usr/share/opentyrian")
        except:
            eslog.error("ERROR: Game assets not installed. You can get them from the Batocera Content Downloader.")
        commandArray = ["opentyrian"]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
