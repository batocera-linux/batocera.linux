#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import batoceraFiles
import sys
import shutil
import controllersConfig
import filecmp

class XeniaGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        wineprefix = batoceraFiles.SAVES + "/xenia-bottle"
        emupath = wineprefix + "/xenia"

        if not os.path.exists(wineprefix):
            os.makedirs(wineprefix)

        # create dir & copy xenia exe to wine bottle as necessary
        if not os.path.exists(emupath):
            shutil.copytree("/usr/xenia", emupath)
        # check binary then copy update xenia exe as necessary
        if not filecmp.cmp("/usr/xenia/xenia.exe", emupath + "/xenia.exe"):
            shutil.copytree("/usr/xenia", emupath, dirs_exist_ok=True)
        
        # create portable txt file to try & stop file spam
        if not os.path.exists(emupath + "/portable.txt"):
            with open(emupath + "/portable.txt", "w") as fp:
                pass
     
        # now setup the command array for the emulator
        if rom == 'config':
            commandArray = ['/usr/wine/lutris/bin/wine64', '/userdata/saves/xenia-bottle/xenia/xenia.exe']
        else:
            commandArray = ['/usr/wine/lutris/bin/wine64', '/userdata/saves/xenia-bottle/xenia/xenia.exe', '--fullscreen', 'z:' + rom]

        return Command.Command(
            array=commandArray,
            env={
                'WINEPREFIX': wineprefix,
                'LD_LIBRARY_PATH': '/usr/lib:/lib32:/usr/wine/lutris/lib/wine',
                'LIBGL_DRIVERS_PATH': '/usr/lib/dri',
                '__NV_PRIME_RENDER_OFFLOAD': '1',
                'WINEESYNC': '1',
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers),
                # hum pw 0.2 and 0.3 are hardcoded, not nice
                'SPA_PLUGIN_DIR': '/usr/lib/spa-0.2:/lib32/spa-0.2',
                'PIPEWIRE_MODULE_DIR': '/usr/lib/pipewire-0.3:/lib32/pipewire-0.3'
            })

    # Show mouse on screen when needed
    # xenia auto-hides
    def getMouseMode(self, config):
        return True
