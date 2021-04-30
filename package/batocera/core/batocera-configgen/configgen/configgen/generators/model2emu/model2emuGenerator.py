#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import batoceraFiles
from utils.logger import eslog
import subprocess
import sys
import shutil
import stat
import configparser

class Model2EmuGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        wineprefix = batoceraFiles.SAVES + "/model2"
        emupath = wineprefix + "/model2emu"

        if not os.path.exists(wineprefix):
            os.makedirs(wineprefix)

        #copy model2emu to /userdata for rw & emulator directory creation reasons
        if not os.path.exists(emupath):
            shutil.copytree("/usr/model2emu", emupath)
            os.chmod(emupath + "/EMULATOR.INI", stat.S_IRWXO)
        
        # install windows libraries required
        if not os.path.exists(wineprefix + "/d3dcompiler_42.done"):
            cmd = ["/usr/wine/winetricks", "d3dcompiler_42"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/lutris/bin:/bin:/usr/bin"
            eslog.log("command: {}".format(str(cmd)))
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.log(out.decode())
            eslog.log(err.decode())
            with open(wineprefix + "/d3dcompiler_42.done", "w") as f:
                f.write("done")

        if not os.path.exists(wineprefix + "/d3dx9_42.done"):
            cmd = ["/usr/wine/winetricks", "d3dx9_42"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/lutris/bin:/bin:/usr/bin"
            eslog.log("command: {}".format(str(cmd)))
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.log(out.decode())
            eslog.log(err.decode())
            with open(wineprefix + "/d3dx9_42.done", "w") as f:
                f.write("done")

        if not os.path.exists(wineprefix + "/d3dcompiler_43.done"):
            cmd = ["/usr/wine/winetricks", "d3dcompiler_43"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/lutris/bin:/bin:/usr/bin"
            eslog.log("command: {}".format(str(cmd)))
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.log(out.decode())
            eslog.log(err.decode())
            with open(wineprefix + "/d3dcompiler_43.done", "w") as f:
                f.write("done")

        if not os.path.exists(wineprefix + "/d3dx9_43.done"):
            cmd = ["/usr/wine/winetricks", "d3dx9_43"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/lutris/bin:/bin:/usr/bin"
            eslog.log("command: {}".format(str(cmd)))
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.log(out.decode())
            eslog.log(err.decode())
            with open(wineprefix + "/d3dx9_43.done", "w") as f:
                f.write("done")
    
        if not os.path.exists(wineprefix + "/d3dx9.done"):
            cmd = ["/usr/wine/winetricks", "d3dx9"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/lutris/bin:/bin:/usr/bin"
            eslog.log("command: {}".format(str(cmd)))
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.log(out.decode())
            eslog.log(err.decode())
            with open(wineprefix + "/d3dx9.done", "w") as f:
                f.write("done")

        if not os.path.exists(wineprefix + "/xact.done"):
            cmd = ["/usr/wine/winetricks", "xact"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/lutris/bin:/bin:/usr/bin"
            eslog.log("command: {}".format(str(cmd)))
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.log(out.decode())
            eslog.log(err.decode())
            with open(wineprefix + "/xact.done", "w") as f:
                f.write("done")

        if not os.path.exists(wineprefix + "/xact_x64.done"):
            cmd = ["/usr/wine/winetricks", "xact_x64"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/lutris/bin:/bin:/usr/bin"
            eslog.log("command: {}".format(str(cmd)))
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.log(out.decode())
            eslog.log(err.decode())
            with open(wineprefix + "/xact_x64.done", "w") as f:
                f.write("done")
        
        # move to the emulator path to ensure configs are saved etc
        os.chdir(emupath)

        # modify the ini file resolution accordingly
        configFileName = emupath + "/EMULATOR.INI"
        Config = configparser.ConfigParser(interpolation=None)
        # to prevent ConfigParser from converting to lower case
        Config.optionxform = str
        if os.path.isfile(configFileName):
            Config.read(configFileName)

        Config.set("Renderer","FullScreenWidth", str(gameResolution["width"]))
        Config.set("Renderer","FullScreenHeight", str(gameResolution["height"]))
        # set ini to use custom resolution and automatically start in fullscreen
        Config.set("Renderer","FullMode", "4")
        Config.set("Renderer","AutoFull", "1")

        with open(configFileName, 'w') as configfile:
            Config.write(configfile)
        
        # now run the emulator
        #commandArray = ["/usr/wine/lutris/bin/wine", "/userdata/saves/model2/model2emu/emulator_multicpu.exe"]
        commandArray = ["/usr/wine/lutris/bin/wine", "explorer", "/desktop=Wine,{}x{}".format(gameResolution["width"], gameResolution["height"]), "/userdata/saves/model2/model2emu/emulator_multicpu.exe"]
        # simplify the rom name (strip the directory & extension)
        romname = rom.replace("/userdata/roms/model2/", "")
        smplromname = romname.replace(".zip", "")
        commandArray.extend([smplromname])

        return Command.Command(
            array=commandArray,
            env={
                "WINEPREFIX": wineprefix,
                "LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine",
                "LIBGL_DRIVERS_PATH": "/lib32/dri"
            })
