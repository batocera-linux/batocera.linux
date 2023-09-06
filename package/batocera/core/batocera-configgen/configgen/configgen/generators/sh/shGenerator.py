#!/usr/bin/env python

from generators.Generator import Generator
import Command
import controllersConfig
import glob

class ShGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):

        # in case of squashfs, the root directory is passed
        shInDir = glob.glob(rom + "/run.sh")
        if len(shInDir) == 1:
            shrom = shInDir[0]
        else:
            shrom = rom

        commandArray = ["/bin/bash", shrom]
        return Command.Command(array=commandArray,env={
            "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)
        })

    def getMouseMode(self, config):
        return True
