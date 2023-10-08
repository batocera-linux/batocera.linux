#!/usr/bin/env python
import Command
from generators.Generator import Generator
import controllersConfig
import os
import batoceraFiles
import subprocess

from utils.logger import get_logger
eslog = get_logger(__name__)

class StellaGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
        # Launch Stella
        commandArray = ["stella " , rom ]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            }
        )
