#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
from settings.unixSettings import UnixSettings
import controllersConfig
import os

CONFIGDIR  = batoceraFiles.CONF + '/GSplus'
CONFIGFILE = CONFIGDIR + '/config.txt'

class GSplusGenerator(Generator):
    def generate(self, system, rom, playersControllers, gameResolution):
        if not os.path.exists(CONFIGDIR):
            os.makedirs(CONFIGDIR)

        config = UnixSettings(CONFIGFILE, separator=' ')

        rombase=os.path.basename(rom)
        romext=os.path.splitext(rombase)[1]
        print ("_____ ROMEXT: "+romext)
        if (romext.lower() == '.dsk'):
            config.save("s6d1", rom)
            config.save("s5d1", '')
            config.save("s7d1", '')
        else: # .po and .2mg
            config.save("s7d1", rom)
            config.save("s5d1", '')
            config.save("s6d1", '')
        config.save("g_cfg_rom_path", batoceraFiles.BIOS)
        # config.save("g_limit_speed", "0")

        config.write()
        commandArray = ["GSplus", "-fullscreen"]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
