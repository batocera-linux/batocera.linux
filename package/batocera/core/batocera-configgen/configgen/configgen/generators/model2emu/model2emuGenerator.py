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

class Model2EmuGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
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
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/d3dcompiler_42.done", "w") as f:
                f.write("done")

        if not os.path.exists(wineprefix + "/d3dx9_42.done"):
            cmd = ["/usr/wine/winetricks", "d3dx9_42"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/lutris/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/d3dx9_42.done", "w") as f:
                f.write("done")

        if not os.path.exists(wineprefix + "/d3dcompiler_43.done"):
            cmd = ["/usr/wine/winetricks", "d3dcompiler_43"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX": wineprefix }
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
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX": wineprefix }
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

        if not os.path.exists(wineprefix + "/xact.done"):
            cmd = ["/usr/wine/winetricks", "xact"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/lutris/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/xact.done", "w") as f:
                f.write("done")

        if not os.path.exists(wineprefix + "/xact_x64.done"):
            cmd = ["/usr/wine/winetricks", "xact_x64"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/lutris/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
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

        # set ini to use custom resolution and automatically start in fullscreen
        Config.set("Renderer","FullScreenWidth", str(gameResolution["width"]))
        Config.set("Renderer","FullScreenHeight", str(gameResolution["height"]))
        Config.set("Renderer","FullMode", "4")
        Config.set("Renderer","AutoFull", "1")

        # now set the emulator features
        if system.isOptSet("fakeGouraud"):
            Config.set("Renderer","FakeGouraud", format(system.config["fakeGouraud"]))
        else:
            Config.set("Renderer","FakeGouraud", "0")
        if system.isOptSet("bilinearFiltering"):
            Config.set("Renderer","Bilinear", format(system.config["bilinearFiltering"]))
        else:
            Config.set("Renderer","Bilinear", "1")
        if system.isOptSet("trilinearFiltering"):
            Config.set("Renderer","Trilinear", format(system.config["trilinearFiltering"]))
        else:
            Config.set("Renderer","Trilinear", "0")
        if system.isOptSet("filterTilemaps"):
            Config.set("Renderer","FilterTilemaps", format(system.config["filterTilemaps"]))
        else:
            Config.set("Renderer","FilterTilemaps", "0")
        if system.isOptSet("forceManaged"):
            Config.set("Renderer","ForceManaged", format(system.config["forceManaged"]))
        else:
            Config.set("Renderer","ForceManaged", "0")
        if system.isOptSet("enableMIP"):
            Config.set("Renderer","AutoMip", format(system.config["enableMIP"]))
        else:
            Config.set("Renderer","AutoMip", "0")
        if system.isOptSet("meshTransparency"):
            Config.set("Renderer","MeshTransparency", format(system.config["meshTransparency"]))
        else:
            Config.set("Renderer","MeshTransparency", "0")
        if system.isOptSet("fullscreenAA"):
            Config.set("Renderer","FSAA", format(system.config["fullscreenAA"]))
        else:
            Config.set("Renderer","FSAA", "0")
        if system.isOptSet("useRawInput"):
            Config.set("Input","UseRawInput", format(system.config["useRawInput"]))
        else:
            Config.set("Input","UseRawInput", "0")
        
        with open(configFileName, 'w') as configfile:
            Config.write(configfile)
        
        # now run the emulator
        commandArray = ["/usr/wine/lutris/bin/wine", "/userdata/saves/model2/model2emu/emulator_multicpu.exe"]
        # simplify the rom name (strip the directory & extension)
        romname = rom.replace("/userdata/roms/model2/", "")
        smplromname = romname.replace(".zip", "")
        commandArray.extend([smplromname])

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
