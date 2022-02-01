#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import batoceraFiles
from utils.logger import get_logger
import subprocess
import sys
import shutil
import stat
import configparser
import controllersConfig

eslog = get_logger(__name__)

class XeniaGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        wineprefix = batoceraFiles.SAVES + "/xenia-bottle"
        emupath = wineprefix + "/xenia"

        if not os.path.exists(wineprefix):
            os.makedirs(wineprefix)

        # copy xenia to /userdata
        if not os.path.exists(emupath):
            shutil.copytree("/usr/xenia", emupath)

        # dependencies
        # japanese font?

        # todo - emulator options?
        # /userdata/system/Xenia/xenia.config.toml

        # todo - controller options?
       
        # now setup the command array for the emulator
        # lutris doesn't produce choppy sound
        commandArray = ['/usr/wine/lutris/bin/wine64', '/userdata/saves/xenia-bottle/xenia/xenia.exe', '--fullscreen', 'z:' + rom]
        # previous commandline option currently crashes xenia now '--gpu="vulkan"',]

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
