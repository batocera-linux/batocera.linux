#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
from settings.unixSettings import UnixSettings
import controllersConfig
import os
from utils.logger import get_logger

eslog = get_logger(__name__)
CONFIGDIR  = batoceraFiles.CONF + '/GSplus'
CONFIGFILE = CONFIGDIR + '/config.txt'

class GSplusGenerator(Generator):
    def generate(self, system, rom, playersControllers, guns, gameResolution):
        if not os.path.exists(CONFIGDIR):
            os.makedirs(CONFIGDIR)

        config = UnixSettings(CONFIGFILE, separator=' ')

        rombase=os.path.basename(rom)
        romext=os.path.splitext(rombase)[1]
        if (romext.lower() in ['.dsk', '.do', '.nib']):
            config.save("s6d1", rom)
            config.save("s5d1", '')
            config.save("s7d1", '')
            config.save("bram1[00]", '00 00 00 01 00 00 0d 06 02 01 01 00 01 00 00 00')
            config.save("bram1[10]", '00 00 07 06 02 01 01 00 00 00 0f 06 06 00 05 06')
            config.save("bram1[20]", '01 00 00 00 00 00 00 01 06 00 00 00 03 02 02 02')
            config.save("bram1[30]", '00 00 00 00 00 00 00 00 00 00 01 02 03 04 05 06')
            config.save("bram1[40]", '07 00 00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d')
            config.save("bram1[50]", '0e 0f ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[60]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[70]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[80]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[90]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[a0]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[b0]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[c0]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[d0]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[e0]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[f0]", 'ff ff ff ff ff ff ff ff ff ff ff ff fe 17 54 bd')
            config.save("bram3[00]", '00 00 00 01 00 00 0d 06 02 01 01 00 01 00 00 00')
            config.save("bram3[10]", '00 00 07 06 02 01 01 00 00 00 0f 06 00 00 05 06')
            config.save("bram3[20]", '01 00 00 00 00 00 00 01 00 00 00 00 05 02 02 00')
            config.save("bram3[30]", '00 00 2d 2d 00 00 00 00 00 00 02 02 02 06 08 00')
            config.save("bram3[40]", '01 02 03 04 05 06 07 0a 00 01 02 03 04 05 06 07')
            config.save("bram3[50]", '08 09 0a 0b 0c 0d 0e 0f 00 00 ff ff ff ff ff ff')
            config.save("bram3[60]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram3[70]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram3[80]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram3[90]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram3[a0]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram3[b0]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram3[c0]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram3[d0]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram3[e0]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram3[f0]", 'ff ff ff ff ff ff ff ff ff ff ff ff 05 cf af 65')
        else: # .po and .2mg
            config.save("s7d1", rom)
            config.save("s5d1", '')
            config.save("s6d1", '')
            config.save("bram1[00]", '00 00 00 01 00 00 0d 06 02 01 01 00 01 00 00 00')
            config.save("bram1[10]", '00 00 07 06 02 01 01 00 00 00 0f 06 06 00 05 06')
            config.save("bram1[20]", '01 00 00 00 00 00 00 01 00 00 00 00 03 02 02 02')
            config.save("bram1[30]", '00 00 00 00 00 00 00 00 08 00 01 02 03 04 05 06')
            config.save("bram1[40]", '07 0a 00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d')
            config.save("bram1[50]", '0e 0f ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[60]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[70]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[80]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[90]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[a0]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[b0]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[c0]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[d0]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[e0]", 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff')
            config.save("bram1[f0]", 'ff ff ff ff ff ff ff ff ff ff ff ff 13 24 b9 8e')
            config.save("bram3[00]", '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
            config.save("bram3[10]", '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
            config.save("bram3[20]", '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
            config.save("bram3[30]", '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
            config.save("bram3[40]", '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
            config.save("bram3[50]", '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
            config.save("bram3[60]", '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
            config.save("bram3[70]", '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
            config.save("bram3[80]", '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
            config.save("bram3[90]", '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
            config.save("bram3[a0]", '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
            config.save("bram3[b0]", '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
            config.save("bram3[c0]", '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
            config.save("bram3[d0]", '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
            config.save("bram3[e0]", '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
            config.save("bram3[f0]", '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
        config.save("g_cfg_rom_path", batoceraFiles.BIOS)
        # config.save("g_limit_speed", "0")

        config.write()
        commandArray = ["GSplus", "-fullscreen"]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
