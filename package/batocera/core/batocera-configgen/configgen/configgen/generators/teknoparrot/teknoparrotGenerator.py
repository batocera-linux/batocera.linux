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

eslog = get_logger(__name__)

class TeknoParrotGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        wineprefix = batoceraFiles.SAVES + "/teknoparrot"
        emupath = wineprefix + "/teknoparrot"

        if not os.path.exists(wineprefix):
            os.makedirs(wineprefix)

        #copy teknoparrot to /userdata for rw & emulator directory creation reasons
        if not os.path.exists(emupath):
            shutil.copytree("/usr/teknoparrot", emupath)
        
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

        if not os.path.exists(wineprefix + "/dotnet462.done"):
            cmd = ["/usr/wine/winetricks", "-q", "dotnet462"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/lutris/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/dotnet462.done", "w") as f:
                f.write("done")
    
        if not os.path.exists(wineprefix + "/d3dx9.done"):
            cmd = ["/usr/wine/winetricks", "-q", "d3dx9"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/lutris/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/d3dx9.done", "w") as f:
                f.write("done")
        
        # set ini to use custom resolution and automatically start in fullscreen

        # now set the emulator features
        
        # now run the emulator
        commandArray = ["/usr/wine/lutris/bin/wine", "/userdata/saves/teknoparrot/teknoparrot/TeknoParrotUi.exe"]
        # simplify the rom name (strip the directory & extension)
        romname = rom.replace("/userdata/roms/teknoparrot/", "")
        commandArray.extend([f"--profile={romname}"])

        return Command.Command(
            array=commandArray,
            env={
                "WINEPREFIX": wineprefix,
                "LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine",
                "LIBGL_DRIVERS_PATH": "/lib32/dri",
                # hum pw 0.2 and 0.3 are hardcoded, not nice
                "SPA_PLUGIN_DIR": "/usr/lib/spa-0.2:/lib32/spa-0.2",
                "PIPEWIRE_MODULE_DIR": "/usr/lib/pipewire-0.3:/lib32/pipewire-0.3"
            })
