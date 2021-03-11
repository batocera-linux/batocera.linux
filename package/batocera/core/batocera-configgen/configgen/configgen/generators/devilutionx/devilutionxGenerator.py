#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig


class DevilutionXGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        commandArray = ["devilutionx", "--data-dir", "/userdata/roms/devilutionx",
                        "--config-dir", "/userdata/system/config/devilutionx",
                        "--save-dir", "/userdata/saves/devilutionx"]
        if not rom.endswith('hellfire.mpq'):
            commandArray.append('--diablo')
        if system.isOptSet('showFPS') and system.getOptBoolean('showFPS') == True:
            commandArray.append("-f")
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
