#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
from shutil import copyfile
import os
import batoceraFiles
import filecmp

redream_file = "/usr/bin/redream"
redreamConfig = batoceraFiles.CONF + "/redream"

class RedreamGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        redream_exec = redreamConfig + "/redream"

        if not os.path.exists(redreamConfig):
            os.makedirs(redreamConfig)

        if not os.path.exists(redream_exec) or not filecmp.cmp(redream_file, redream_exec):
            copyfile(redream_file, redream_exec)
            os.chmod(redream_exec, 0o0775)

        commandArray = [redream_exec, rom]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
