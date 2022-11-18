#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import batoceraFiles
import sys
import shutil
import controllersConfig
import filecmp
import subprocess
from utils.logger import get_logger

eslog = get_logger(__name__)

class XeniaGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        wineprefix = batoceraFiles.SAVES + "/xenia-bottle"
        emupath = wineprefix + "/xenia"
        canarypath = wineprefix + "/xenia-canary"

        core = system.config["core"]

        if not os.path.exists(wineprefix):
            os.makedirs(wineprefix)

        # create dir & copy xenia exe to wine bottle as necessary
        if not os.path.exists(emupath):
            shutil.copytree("/usr/xenia", emupath)
        if not os.path.exists(canarypath):
            shutil.copytree("/usr/xenia-canary", canarypath)
        # check binary then copy updated xenia exe's as necessary
        if not filecmp.cmp("/usr/xenia/xenia.exe", emupath + "/xenia.exe"):
            shutil.copytree("/usr/xenia", emupath, dirs_exist_ok=True)
        if not filecmp.cmp("/usr/xenia-canary/xenia_canary.exe", canarypath + "/xenia_canary.exe"):
            shutil.copytree("/usr/xenia-canary", canarypath, dirs_exist_ok=True)
        
        # create portable txt file to try & stop file spam
        if not os.path.exists(emupath + "/portable.txt"):
            with open(emupath + "/portable.txt", "w") as fp:
                pass
        if not os.path.exists(canarypath + "/portable.txt"):
            with open(canarypath + "/portable.txt", "w") as fp:
                pass

        # install windows libraries required
        if not os.path.exists(wineprefix + "/vcrun2019.done"):
            cmd = ["/usr/wine/winetricks", "-q", "vcrun2019"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/lutris/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/vcrun2019.done", "w") as f:
                f.write("done")
     
        # now setup the command array for the emulator
        if rom == 'config':
            if core == 'xenia-canary':
                commandArray = ['/usr/wine/lutris/bin/wine64', '/userdata/saves/xenia-bottle/xenia-canary/xenia_canary.exe']
            else:
                commandArray = ['/usr/wine/lutris/bin/wine64', '/userdata/saves/xenia-bottle/xenia/xenia.exe']
        else:
            if core == 'xenia-canary':
                commandArray = ['/usr/wine/lutris/bin/wine64', '/userdata/saves/xenia-bottle/xenia-canary/xenia_canary.exe', '--fullscreen', 'z:' + rom]
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
                'SDL_JOYSTICK_HIDAPI': '0',
                # hum pw 0.2 and 0.3 are hardcoded, not nice
                'SPA_PLUGIN_DIR': '/usr/lib/spa-0.2:/lib32/spa-0.2',
                'PIPEWIRE_MODULE_DIR': '/usr/lib/pipewire-0.3:/lib32/pipewire-0.3'
            })

    # Show mouse on screen when needed
    # xenia auto-hides
    def getMouseMode(self, config):
        return True
