#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import batoceraFiles
import subprocess
import sys
import shutil
import stat
import configparser
import filecmp
from utils.logger import get_logger

eslog = get_logger(__name__)

class BigPEmuGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        wineprefix = batoceraFiles.SAVES + "/bigpemu-bottle"
        emupath = wineprefix + "/bigpemu"

        if not os.path.exists(wineprefix):
            os.makedirs(wineprefix)

        #copy bigpemu files to wine bottle
        if not os.path.exists(emupath):
            shutil.copytree("/usr/bigpemu", emupath)
        
        # check we have the latest version in the wine bottle
        if not filecmp.cmp("/usr/bigpemu/BigPEmu.exe", emupath + "/BigPEmu.exe"):
            shutil.copytree("/usr/bigpemu", emupath, dirs_exist_ok=True)

        # install windows libraries required
        if not os.path.exists(wineprefix + "/d3dcompiler_43.done"):
            cmd = ["/usr/wine/winetricks", "d3dcompiler_43"]
            env = {"LD_LIBRARY_PATH": "/lib:/usr/lib:/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/lutris/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/d3dcompiler_43.done", "w") as f:
                f.write("done")

        if not os.path.exists(wineprefix + "/d3dx9_43.done"):
            cmd = ["/usr/wine/winetricks", "d3dx9_43"]
            env = {"LD_LIBRARY_PATH": "/lib:/usr/lib:/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/lutris/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/d3dx9_43.done", "w") as f:
                f.write("done")
    
        if not os.path.exists(wineprefix + "/d3dx9.done"):
            cmd = ["/usr/wine/winetricks", "d3dx9"]
            env = {"LD_LIBRARY_PATH": "/lib:/usr/lib:/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX": wineprefix }
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
      
        # todo: some config?
        # /userdata/saves/bigpemu-bottle/drive_c/users/root/AppData/Roaming/BigPEmu/BigPEmuConfig.bigpcfg

        # now run the emulator
        commandArray = ["/usr/wine/lutris/bin/wine", "/userdata/saves/bigpemu-bottle/bigpemu/BigPEmu.exe", rom]
        # we use a 64-bit wine bottle
        return Command.Command(
            array=commandArray,
            env={
                "WINEPREFIX": wineprefix,
                "LD_LIBRARY_PATH": "/lib:/usr/lib:/lib32:/usr/wine/lutris/lib/wine",
                "LIBGL_DRIVERS_PATH": "/usr/lib/dri:/lib32/dri",
                "SPA_PLUGIN_DIR": "/usr/lib/spa-0.2:/lib32/spa-0.2",
                "PIPEWIRE_MODULE_DIR": "/usr/lib/pipewire-0.3:/lib32/pipewire-0.3"
            })
