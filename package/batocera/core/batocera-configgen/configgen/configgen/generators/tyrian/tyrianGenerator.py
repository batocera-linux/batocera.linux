#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
import os
from utils.logger import get_logger
eslog = get_logger(__name__)

class TyrianGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
        try:
            os.chdir("/userdata/roms/tyrian/data")
        except:
            eslog.error("ERROR: Game assets not installed. You can get them from the Batocera Content Downloader.")
        commandArray = ["opentyrian"]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
