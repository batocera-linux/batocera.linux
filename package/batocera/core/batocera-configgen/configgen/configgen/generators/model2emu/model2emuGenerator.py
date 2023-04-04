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
from pathlib import Path, PureWindowsPath
import configparser

eslog = get_logger(__name__)

class Model2EmuGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        wineprefix = batoceraFiles.SAVES + "/model2"
        emupath = wineprefix + "/model2emu"
        rompath = "/userdata/roms/model2"

        if not os.path.exists(wineprefix):
            os.makedirs(wineprefix)

        #copy model2emu to /userdata for rw & emulator directory creation reasons
        if not os.path.exists(emupath):
            shutil.copytree("/usr/model2emu", emupath)
            os.chmod(emupath + "/EMULATOR.INI", stat.S_IRWXO)
        
        # install windows libraries required
        if not os.path.exists(wineprefix + "/d3dx9.done"):
            cmd = ["/usr/wine/winetricks", "-q", "d3dx9"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/proton/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/proton/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/d3dx9.done", "w") as f:
                f.write("done")
        
        if not os.path.exists(wineprefix + "/d3dcompiler_42.done"):
            cmd = ["/usr/wine/winetricks", "-q", "d3dcompiler_42"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/proton/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/proton/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/d3dcompiler_42.done", "w") as f:
                f.write("done")
        
        if not os.path.exists(wineprefix + "/d3dx9_42.done"):
            cmd = ["/usr/wine/winetricks", "-q", "d3dx9_42"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/proton/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/proton/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/d3dx9_42.done", "w") as f:
                f.write("done")
        
        if not os.path.exists(wineprefix + "/xact.done"):
            cmd = ["/usr/wine/winetricks", "-q", "xact"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/proton/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/proton/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/xact.done", "w") as f:
                f.write("done")
        
        if not os.path.exists(wineprefix + "/xact_x64.done"):
            cmd = ["/usr/wine/winetricks", "-q", "xact_x64"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/proton/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/proton/bin:/bin:/usr/bin"
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
        
        # add subdirectories
        dirnum = 1 # existing rom path
        for x in os.listdir(rompath):
            possibledir = str(rompath + "/" + x)
            if os.path.isdir(possibledir) and x != "images":
                dirnum = dirnum +1
                # convert to windows friendly name
                subdir = PureWindowsPath(possibledir)
                # add path to ini file
                Config.set("RomDirs",f"Dir{dirnum}", f"Z:{subdir}")
        
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
        
        # set the environment variables
        environment = {
            "WINEPREFIX": wineprefix,
            "LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine",
            "LIBGL_DRIVERS_PATH": "/lib32/dri",
            "SPA_PLUGIN_DIR": "/usr/lib/spa-0.2:/lib32/spa-0.2",
            "PIPEWIRE_MODULE_DIR": "/usr/lib/pipewire-0.3:/lib32/pipewire-0.3"
        }

        # check if software render option is chosen
        if system.isOptSet("model2Software") and system.config["model2Software"] == "1":
            environment = {
            "WINEPREFIX": wineprefix,
            "LD_LIBRARY_PATH": "/lib32:/usr/wine/lutris/lib/wine",
            "LIBGL_DRIVERS_PATH": "/lib32/dri",
            "SPA_PLUGIN_DIR": "/usr/lib/spa-0.2:/lib32/spa-0.2",
            "PIPEWIRE_MODULE_DIR": "/usr/lib/pipewire-0.3:/lib32/pipewire-0.3",
            "__GLX_VENDOR_LIBRARY_NAME": "mesa",
            "MESA_LOADER_DRIVER_OVERRIDE": "llvmpipe",
            "GALLIUM_DRIVER": "llvmpipe"
            }

        # now run the emulator
        commandArray = ["/usr/wine/proton/bin/wine", "/userdata/saves/model2/model2emu/emulator_multicpu.exe"]
        # simplify the rom name (strip the directory & extension)
        if rom != 'config':
            romname = rom.replace("/userdata/roms/model2/", "")
            smplromname = romname.replace(".zip", "")
            rom = smplromname.split('/', 1)[-1]
            commandArray.extend([rom])
        
        return Command.Command(array=commandArray, env=environment)
