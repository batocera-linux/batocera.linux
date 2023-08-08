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

def modify_lua_widescreen(file_path, condition):
    with open(file_path, 'r') as lua_file:
        lines = lua_file.readlines()
        
    modified_lines = []
    for line in lines:
        if condition == "True":
            if "wide=false" in line:
                modified_line = line.replace("wide=false", "wide=true")
            else:
                modified_line = line  # No change
            modified_lines.append(modified_line)
        else:
            if "wide=true" in line:
                modified_line = line.replace("wide=true", "wide=false")
            else:
                modified_line = line  # No change
            modified_lines.append(modified_line)
    
    with open(file_path, 'w') as lua_file:
        lua_file.writelines(modified_lines)

def modify_lua_scanlines(file_path, condition):
    with open(file_path, 'r') as lua_file:
        original_lines = lua_file.readlines()

    modified_lines = []
    found_test_surface_line = False
    scanlines_line_added = False

    for line in original_lines:
        if "TestSurface = Video_CreateSurfaceFromFile" in line:
            found_test_surface_line = True
            modified_lines.append(line)
            if "Options.scanlines.value=" not in line and not scanlines_line_added:
                modified_lines.append(f'\tOptions.scanlines.value={"1" if condition == "True" else "0"}\r\n')
                scanlines_line_added = True
        elif "Options.scanlines.value=" in line:
            if condition == "True":
                modified_lines.append(line.replace("Options.scanlines.value=0", "Options.scanlines.value=1"))
            elif condition == "False":
                modified_lines.append(line.replace("Options.scanlines.value=1", "Options.scanlines.value=0"))
        else:
            modified_lines.append(line)

    with open(file_path, 'w') as lua_file:
        lua_file.writelines(modified_lines)


class Model2EmuGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        wineprefix = batoceraFiles.SAVES + "/model2"
        emupath = wineprefix + "/model2emu"
        rompath = "/userdata/roms/model2/"

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

        commandArray = ["/usr/wine/proton/bin/wine", emupath + "/emulator_multicpu.exe"]
        # simplify the rom name (strip the directory & extension)
        if rom != 'config':
            romname = rom.replace(rompath, "")
            smplromname = romname.replace(".zip", "")
            rom = smplromname.split('/', 1)[-1]
            commandArray.extend([rom])

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
            possibledir = str(rompath + x)
            if os.path.isdir(possibledir) and x != "images":
                dirnum = dirnum +1
                # convert to windows friendly name
                subdir = PureWindowsPath(possibledir)
                # add path to ini file
                Config.set("RomDirs",f"Dir{dirnum}", f"Z:{subdir}")
        
        # set ini to use chosen resolution and automatically start in fullscreen
        Config.set("Renderer","FullScreenWidth", str(gameResolution["width"]))
        Config.set("Renderer","FullScreenHeight", str(gameResolution["height"]))
        if system.isOptSet("renderRes"):
            Config.set("Renderer","FullMode", format(system.config["renderRes"]))
        else:
            Config.set("Renderer","FullMode", "4")
        Config.set("Renderer","AutoFull", "1")
        # widescreen
        lua_file_path = emupath + "/scripts/" + rom + ".lua"
        if system.isOptSet("ratio"):
            if os.path.exists(lua_file_path):
                modify_lua_widescreen(lua_file_path, system.config["ratio"])
        else:
            if os.path.exists(lua_file_path):
                modify_lua_widescreen(lua_file_path, "False")
        # scanlines
        if system.isOptSet("scanlines"):
            if os.path.exists(lua_file_path):
                modify_lua_scanlines(lua_file_path, system.config["scanlines"])
        else:
            if os.path.exists(lua_file_path):
                modify_lua_scanlines(lua_file_path, "False")
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
        if system.isOptSet("crossHairs"):
            Config.set("Renderer","DrawCross", format(system.config["crossHairs"]))
        else:
            Config.set("Renderer","DrawCross", "1")
        
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
            environment.update({
                "__GLX_VENDOR_LIBRARY_NAME": "mesa",
                "MESA_LOADER_DRIVER_OVERRIDE": "llvmpipe",
                "GALLIUM_DRIVER": "llvmpipe"
            })

        # now run the emulator        
        return Command.Command(array=commandArray, env=environment)
