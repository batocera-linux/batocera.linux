#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
from shutil import copyfile
import os

class RedreamGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        configdir = "/userdata/system/configs/redream"
        if not os.path.exists(configdir):
            os.makedirs(configdir)

        copyfile("/usr/bin/redream", configdir + "/redream")
        os.chmod(configdir + "/redream", 0o0775)

        commandArray = [configdir + "/redream", rom]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
