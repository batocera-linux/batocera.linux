#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
from shutil import copyfile
import os

class RedreamGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        gta3_dir = "/userdata/roms/ports/GTA III"
        gta_miami_dir = "/userdata/roms/ports/GTA Vice City"
        if not os.path.exists(gta3_dir):
            os.makedirs(gta3_dir)

        copyfile("/usr/bin/re3", gta3_dir + "/re3")
        os.chmod(gta3_dir + "/re3", 0o0775)

        commandArray = [gta3_dir + "/re3"]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
