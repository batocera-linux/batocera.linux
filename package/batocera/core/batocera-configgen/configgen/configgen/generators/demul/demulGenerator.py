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
from pathlib import Path, PureWindowsPath
from distutils.dir_util import copy_tree

eslog = get_logger(__name__)

class DemulGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        wineprefix = batoceraFiles.SAVES + "/demul"
        emupath = wineprefix + "/demul"
        bottlewinpath = wineprefix + "/drive_c/windows" 

        if not os.path.exists(wineprefix):
            os.makedirs(wineprefix)

        # copy demulemu to /userdata for rw & emulator directory creation reasons
        if not os.path.exists(emupath):
            shutil.copytree("/usr/demul", emupath)
            # add dxvk dll's
            copy_tree("/usr/wine/dxvk/x64/", bottlewinpath + "/system32/")
            copy_tree("/usr/wine/dxvk/x32/", bottlewinpath + "/syswow64/")
                            
        # determine what system to define for demul
        # -run=<name>		run specified system (dc, naomi, awave, hikaru, gaelco, cave3rd)
        if "naomi" in rom:
            demulsystem = "naomi"
        elif "hikaru" in rom:
            demulsystem = "hikaru"
        elif "gaelco" in rom:
            demulsystem = "gaelco"
        elif "cave3rd" in rom:
            demulsystem = "cave3rd"
        elif "dreamcast" in rom:
            demulsystem = "dc"
        elif "atomiswave" in rom:
            demulsystem = "awave"

        # remove the rom path & extension to simplify the rom name when needed
        # -rom=<romname>	run specified system rom from the rom path defined in Demul.ini
        # or -image=<full image path> for dreamcast
        if demulsystem == "naomi":
            if "naomi2" in rom:
                romname = rom.replace("/userdata/roms/naomi2/", "")
            else:
                romname = rom.replace("/userdata/roms/naomi/", "")
        elif demulsystem == "hikaru":
            romname = rom.replace("/userdata/roms/hikaru/", "")
        elif demulsystem == "gaelco":
            romname = rom.replace("/userdata/roms/gaelco/", "")
        elif demulsystem == "cave3rd":
            romname = rom.replace("/userdata/roms/cave3rd/", "")
        elif demulsystem == "awave":
            romname = rom.replace("/userdata/roms/atomiswave/", "")

        # move to the emulator path to ensure configs are saved etc
        os.chdir(emupath)
        configFileName = emupath + "/Demul.ini"
        Config = configparser.ConfigParser(interpolation=None)
        Config.optionxform = str

        if os.path.exists(configFileName):
            try:
                with open(configFileName, 'r', encoding='utf_8_sig') as fp:
                    Config.read_file(fp)
            except:
                pass
        
        # add rom & bios paths to Demul.ini
        nvram = Path("/userdata/saves/demul/demul/nvram/")
        nvram_path_on_windows = PureWindowsPath(nvram)
        roms0 = Path("/userdata/roms/naomi2/")
        roms0_path_on_windows = PureWindowsPath(roms0)
        roms1 = Path("/userdata/bios/")
        roms1_path_on_windows = PureWindowsPath(roms1)
        roms2 = Path("/userdata/roms/hikaru")
        roms2_path_on_windows = PureWindowsPath(roms2)
        roms3 = Path("/userdata/roms/gaelco")
        roms3_path_on_windows = PureWindowsPath(roms3)
        roms4 = Path("/userdata/roms/cave3rd")
        roms4_path_on_windows = PureWindowsPath(roms4)
        roms5 = Path("/userdata/roms/dreamcast")
        roms5_path_on_windows = PureWindowsPath(roms5)
        roms6 = Path("/userdata/roms/atomiswave")
        roms6_path_on_windows = PureWindowsPath(roms6)
        roms7 = Path("/userdata/roms/naomi")
        roms7_path_on_windows = PureWindowsPath(roms7)
        plugins = Path("/userdata/saves/demul/demul/plugins/")
        plugins_path_on_windows = PureWindowsPath(plugins)
            
        if not Config.has_section("files"):
            Config.add_section("files")
        Config.set("files", "nvram", f"Z:{nvram_path_on_windows}")
        Config.set("files", "roms0", f"Z:{roms0_path_on_windows}")
        Config.set("files", "romsPathsCount", "8")
        Config.set("files", "roms1", f"Z:{roms1_path_on_windows}")
        Config.set("files", "roms2", f"Z:{roms2_path_on_windows}")
        Config.set("files", "roms3", f"Z:{roms3_path_on_windows}")
        Config.set("files", "roms4", f"Z:{roms4_path_on_windows}")
        Config.set("files", "roms5", f"Z:{roms5_path_on_windows}")
        Config.set("files", "roms6", f"Z:{roms6_path_on_windows}")
        Config.set("files", "roms7", f"Z:{roms7_path_on_windows}")

        if not Config.has_section("plugins"):
            Config.add_section("plugins")
        Config.set("plugins", "directory", f"Z:{plugins_path_on_windows}")
        Config.set("plugins", "spu", "spuDemul.dll")
        Config.set("plugins", "pad", "padDemul.dll")
        Config.set("plugins", "net", "netDemul.dll")
        # gaelco won't work with the new DX11 plugin
        if demulsystem == "gaelco":
            Config.set("plugins", "gpu", "gpuDX11old.dll")
        else:
            Config.set("plugins", "gpu", "gpuDX11.dll")

        # dreamcast needs the full path & cdi or gdi image extensions
        # check if we need to change the gdr plugin.
        if demulsystem == "dc":
            if ".chd" in rom:
                Config.set("plugins", "gdr", "gdrCHD.dll")
            else:
                Config.set("plugins", "gdr", "gdrImage.dll")
        # demul supports zip & 7zip romset extensions
        elif ".zip" in romname:
            smplromname = romname.replace(".zip", "")
            Config.set("plugins", "gdr", "gdrImage.dll")
        elif ".7z" in romname:
            smplromname = romname.replace(".7z", "")
            Config.set("plugins", "gdr", "gdrImage.dll")

        with open(configFileName, 'w', encoding='utf_8_sig') as configfile:
            Config.write(configfile)

        # add the windows rom path if dreamcast
        if demulsystem == "dc":
            dcrom_windows = PureWindowsPath(rom)
            # add Z:
            dcpath = f"Z:{dcrom_windows}"

        # adjust fullscreen & resolution to gpuDX11.ini
        if demulsystem == "gaelco":
            configFileName = emupath + "/gpuDX11old.ini"
        else:
            configFileName = emupath + "/gpuDX11.ini"
        Config = configparser.ConfigParser(interpolation=None)
        Config.optionxform = str
        if os.path.exists(configFileName):
            try:
                with open(configFileName, 'r', encoding='utf_8_sig') as fp:
                    Config.read_file(fp)
            except:
                pass
        
        # set to be always fullscreen
        if not Config.has_section("main"):
            Config.add_section("main")
        Config.set("main","UseFullscreen", "1")
        # set resolution
        if not Config.has_section("resolution"):
            Config.add_section("resolution")
        # force 640x480 on gaelco
        if demulsystem == "gaelco":
            Config.set("resolution", "Width", "640")
            Config.set("resolution", "Height", "480")
        else:
            Config.set("resolution", "Width", str(gameResolution["width"]))
            Config.set("resolution", "Height", str(gameResolution["height"]))

        # now set the batocera options
        if system.isOptSet("demulRatio"):
            Config.set("main", "aspect", format(system.config["demulRatio"]))
        else:
            Config.set("main", "aspect", "1")

        if system.isOptSet("demulVSync"):
            Config.set("main", "Vsync", format(system.config["demulVSync"]))
        else:
            Config.set("main", "Vsync", "0")
     
        with open(configFileName, 'w', encoding='utf_8_sig') as configfile:
            Config.write(configfile)
              
        # now setup the command array for the emulator
        commandArray = ["/usr/wine/proton/bin/wine", "/userdata/saves/demul/demul/demul.exe"]
        # add system to command array
        commandArray.extend([f"-run={demulsystem}"])
        # add rom to the command array if not dreamcast
        if demulsystem == "dc":
            commandArray.extend([f"-image={dcpath}"])
        else:
            commandArray.extend([f"-rom={smplromname}"])

        return Command.Command(
            array=commandArray,
            env={
                "WINEPREFIX": wineprefix,
                "LD_LIBRARY_PATH": "/lib32:/usr/wine/proton/lib/wine",
                "LIBGL_DRIVERS_PATH": "/lib32/dri",
                "WINEDLLOVERRIDES": "d3d11=n",
                # hum pw 0.2 and 0.3 are hardcoded, not nice
                "SPA_PLUGIN_DIR": "/usr/lib/spa-0.2:/lib32/spa-0.2",
                "PIPEWIRE_MODULE_DIR": "/usr/lib/pipewire-0.3:/lib32/pipewire-0.3"
            })
