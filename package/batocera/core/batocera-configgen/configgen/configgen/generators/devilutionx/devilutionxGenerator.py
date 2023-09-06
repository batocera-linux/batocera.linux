#!/usr/bin/env python

import os
import Command
from generators.Generator import Generator
import controllersConfig


class DevilutionXGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
        configDir = '/userdata/system/configs/devilutionx'
        saveDir = '/userdata/saves/devilutionx'
        os.makedirs(configDir, exist_ok=True)
        os.makedirs(saveDir, exist_ok=True)

        commandArray = ['devilutionx', '--data-dir', '/userdata/roms/devilutionx',
                        '--config-dir', configDir, '--save-dir', saveDir]
        if rom.endswith('hellfire.mpq'):
            commandArray.append('--hellfire')
        elif rom.endswith('spawn.mpq'):
            commandArray.append('--spawn')
        else:
            commandArray.append('--diablo')

        if system.isOptSet('showFPS') and system.getOptBoolean('showFPS') == True:
            commandArray.append('-f')
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
