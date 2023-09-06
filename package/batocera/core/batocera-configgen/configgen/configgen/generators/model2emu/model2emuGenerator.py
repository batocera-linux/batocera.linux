#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import batoceraFiles
import subprocess
import sys
import shutil
import stat
from pathlib import Path, PureWindowsPath
import configparser
import filecmp
import controllersConfig

from utils.logger import get_logger
eslog = get_logger(__name__)

class Model2EmuGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
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
        
        # for existing bottles we want to ensure files are updated as necessary
        copy_updated_files("/usr/model2emu/scripts", emupath + "/scripts")

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
        if system.isOptSet("model2_renderRes"):
            Config.set("Renderer","FullMode", format(system.config["model2_renderRes"]))
        else:
            Config.set("Renderer","FullMode", "4")
        Config.set("Renderer","AutoFull", "1")
        Config.set("Renderer","ForceSync", "1")
        # widescreen
        lua_file_path = emupath + "/scripts/" + rom + ".lua"
        if system.isOptSet("model2_ratio"):
            if os.path.exists(lua_file_path):
                modify_lua_widescreen(lua_file_path, system.config["model2_ratio"])
        else:
            if os.path.exists(lua_file_path):
                modify_lua_widescreen(lua_file_path, "False")
        # scanlines
        if system.isOptSet("model2_scanlines"):
            if os.path.exists(lua_file_path):
                modify_lua_scanlines(lua_file_path, system.config["model2_scanlines"])
        else:
            if os.path.exists(lua_file_path):
                modify_lua_scanlines(lua_file_path, "False")
        # sinden - check if rom is a gun game
        known_gun_roms = ["bel", "gunblade", "hotd", "rchase2", "vcop", "vcop2", "vcopa"]
        if rom in known_gun_roms:
            if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) > 0:
                for gun in guns:
                    if guns[gun]["need_borders"]:
                        if os.path.exists(lua_file_path):
                            bordersSize = controllersConfig.gunsBordersSizeName(guns, system.config)
                            # add more intelligence for lower resolution screens to avoid massive borders
                            if bordersSize == "thin":
                                thickness = "1"
                            elif bordersSize == "medium":
                                if gameResolution["width"] <= 640:
                                    thickness = "1"  # thin
                                elif 640 < gameResolution["width"] <= 1080:
                                    thickness = "2"
                                else:
                                    thickness = "2"
                            else:
                                if gameResolution["width"] << 1080:
                                    thickness = "2"
                                else:
                                    thickness = "3"
                            
                            modify_lua_sinden(lua_file_path, "true", thickness)
                    else:
                        modify_lua_sinden(lua_file_path, "false", "0")

        # now set the other emulator features
        if system.isOptSet("model2_fakeGouraud"):
            Config.set("Renderer","FakeGouraud", format(system.config["model2_fakeGouraud"]))
        else:
            Config.set("Renderer","FakeGouraud", "0")
        if system.isOptSet("model2_bilinearFiltering"):
            Config.set("Renderer","Bilinear", format(system.config["model2_bilinearFiltering"]))
        else:
            Config.set("Renderer","Bilinear", "1")
        if system.isOptSet("model2_trilinearFiltering"):
            Config.set("Renderer","Trilinear", format(system.config["model2_trilinearFiltering"]))
        else:
            Config.set("Renderer","Trilinear", "0")
        if system.isOptSet("model2_filterTilemaps"):
            Config.set("Renderer","FilterTilemaps", format(system.config["model2_filterTilemaps"]))
        else:
            Config.set("Renderer","FilterTilemaps", "0")
        if system.isOptSet("model2_forceManaged"):
            Config.set("Renderer","ForceManaged", format(system.config["model2_forceManaged"]))
        else:
            Config.set("Renderer","ForceManaged", "0")
        if system.isOptSet("model2_enableMIP"):
            Config.set("Renderer","AutoMip", format(system.config["model2_enableMIP"]))
        else:
            Config.set("Renderer","AutoMip", "0")
        if system.isOptSet("model2_meshTransparency"):
            Config.set("Renderer","MeshTransparency", format(system.config["model2_meshTransparency"]))
        else:
            Config.set("Renderer","MeshTransparency", "0")
        if system.isOptSet("model2_fullscreenAA"):
            Config.set("Renderer","FSAA", format(system.config["model2_fullscreenAA"]))
        else:
            Config.set("Renderer","FSAA", "0")
        if system.isOptSet("model2_useRawInput"):
            Config.set("Input","UseRawInput", format(system.config["model2_useRawInput"]))
        else:
            Config.set("Input","UseRawInput", "0")
        if system.isOptSet("model2_crossHairs"):
            Config.set("Renderer","DrawCross", format(system.config["model2_crossHairs"]))
        else:
            for gun in guns:
                if guns[gun]["need_cross"]:
                    Config.set("Renderer","DrawCross", "1")
                else:
                    Config.set("Renderer","DrawCross", "0")
        
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
        if system.isOptSet("model2_Software") and system.config["model2_Software"] == "1":
            environment.update({
                "__GLX_VENDOR_LIBRARY_NAME": "mesa",
                "MESA_LOADER_DRIVER_OVERRIDE": "llvmpipe",
                "GALLIUM_DRIVER": "llvmpipe"
            })

        # now run the emulator        
        return Command.Command(array=commandArray, env=environment)


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

def modify_lua_sinden(file_path, condition, thickness):
    with open(file_path, 'r') as lua_file:
        original_lines = lua_file.readlines()

    modified_lines = []
    found_test_surface_line = False
    sinden_line_added = False

    for line in original_lines:
        if "TestSurface = Video_CreateSurfaceFromFile" in line:
            found_test_surface_line = True
            modified_lines.append(line)
            if "Options.bezels.value=" not in line and not sinden_line_added:
                modified_lines.append(f'\tOptions.bezels.value={"0" if condition == "False" else thickness}\r\n')
                sinden_line_added = True
        elif "Options.bezels.value=" in line and not sinden_line_added:
            modified_lines.append(line.replace("Options.bezels.value=", f'Options.bezels.value={thickness}\r\n'))
        else:
            modified_lines.append(line)

    with open(file_path, 'w') as lua_file:
        lua_file.writelines(modified_lines)

def copy_updated_files(source_path, destination_path):
    dcmp = filecmp.dircmp(source_path, destination_path)
    
    # Copy missing files and files needing updates from source to destination
    for name in dcmp.left_only + dcmp.diff_files:
        src = os.path.join(source_path, name)
        dst = os.path.join(destination_path, name)
        
        if os.path.isdir(src):
            shutil.copytree(src, dst)
            eslog.debug(f"Copying directory {src} to {dst}")
        else:
            shutil.copy2(src, dst)
            eslog.debug(f"Copying file {src} to {dst}")
