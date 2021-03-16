#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
from shutil import copyfile
import os

class DrasticGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        configdir = "/userdata/system/configs/drastic"
        if not os.path.exists(configdir):
            os.makedirs(configdir)

        copyfile("/usr/bin/drastic", configdir + "/drastic")
        os.chmod(configdir + "/drastic", 0o0775)

        commandArray = [configdir + "/drastic", rom]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
