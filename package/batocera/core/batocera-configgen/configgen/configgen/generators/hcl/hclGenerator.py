#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
import os
from utils.logger import get_logger
eslog = get_logger(__name__)

class HclGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
        try:
            os.chdir("/userdata/roms/hcl/data/map")
            os.chdir("/userdata/roms/hcl/")
        except:
            eslog.error("ERROR: Game assets not installed. You can get them from the Batocera Content Downloader.")
        commandArray = ["hcl", "-d"]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
