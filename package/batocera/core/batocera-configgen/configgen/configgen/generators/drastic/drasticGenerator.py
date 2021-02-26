#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
from shutil import copyfile
import os
import shutil

class DrasticGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        configdir = "/userdata/system/configs/drastic"
        if not os.path.exists(configdir):
            shutil.copytree("/usr/share/drastic", configdir)

        copyfile("/usr/bin/drastic", configdir + "/drastic")
        os.chmod(configdir + "/drastic", 0o0775)
        os.chdir(configdir)

        commandArray = [configdir + "/drastic", rom]
        return Command.Command(
            array=commandArray,
            env={
                'LIB_FB': '3',
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
