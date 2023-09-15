#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
from settings.unixSettings import UnixSettings
import controllersConfig
import os
from utils.logger import get_logger

eslog = get_logger(__name__)
CONFIGDIR  = batoceraFiles.CONF + '/applewin'
CONFIGFILE = CONFIGDIR + '/config.txt'

class AppleWinGenerator(Generator):
    def generate(self, system, rom, playersControllers, guns, gameResolution):
        if not os.path.exists(CONFIGDIR):
            os.makedirs(CONFIGDIR)

        config = UnixSettings(CONFIGFILE, separator=' ')

        rombase=os.path.basename(rom)
        romext=os.path.splitext(rombase)[1]

        config.write()
        commandArray = ["applewin" ]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
