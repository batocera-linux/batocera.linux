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

eslog = get_logger(__name__)

class DemulGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        wineprefix = batoceraFiles.SAVES + "/demul"
        emupath = wineprefix + "/demul"

        if not os.path.exists(wineprefix):
            os.makedirs(wineprefix)

        # copy demulemu to /userdata for rw & emulator directory creation reasons
        if not os.path.exists(emupath):
            shutil.copytree("/usr/demul", emupath)
        
        # get directx11
        if not os.path.exists(wineprefix + "/d3dx11_43.done"):
            cmd = ["/usr/wine/winetricks", "d3dx11_43"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/proton/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/proton/bin:/bin:/usr/bin"
            eslog.debug("command: {}".format(str(cmd)))
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/d3dx11_43.done", "w") as f:
                f.write("done")

        # get Visual C ++ 2010 Redistributable Package
        if not os.path.exists(wineprefix + "/vcrun2010.done"):
            cmd = ["/usr/wine/winetricks", "-q", "vcrun2010"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/proton/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/proton/bin:/bin:/usr/bin"
            eslog.debug("command: {}".format(str(cmd)))
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/vcrun2010.done", "w") as f:
                f.write("done")
              
        # move to the emulator path to ensure configs are saved etc
        os.chdir(emupath)

        configFileName = emupath + "/Demul.ini"
        Config = configparser.ConfigParser(interpolation=None)
        Config.optionxform = str
        if os.path.exists(configFileName):
            try:
                with io.open(configFileName, 'r', encoding='utf_8_sig') as fp:
                    Config.readfp(fp)
            except:
                pass
        
        if not os.path.isfile(configFileName):
            # add rom & bios paths to Demul.ini
            nvram = Path("/userdata/saves/demul/demul/nvram/")
            nvram_path_on_windows = PureWindowsPath(nvram)
            roms0 = Path("/userdata/roms/naomi2/")
            roms0_path_on_windows = PureWindowsPath(roms0)
            roms1 = Path("/userdata/bios/")
            roms1_path_on_windows = PureWindowsPath(roms1)
            plugins = Path("/userdata/saves/demul/demul/plugins/")
            plugins_path_on_windows = PureWindowsPath(plugins)
            
            if not Config.has_section("files"):
                Config.add_section("files")
            Config.set("files", "nvram", "Z:{}".format(nvram_path_on_windows))
            Config.set("files", "roms0", "Z:{}".format(roms0_path_on_windows))
            Config.set("files", "romsPathsCount", "2")
            Config.set("files", "roms1", "Z:{}".format(roms1_path_on_windows))

            if not Config.has_section("plugins"):
                Config.add_section("plugins")
            Config.set("plugins", "directory", "Z:{}".format(plugins_path_on_windows))
            Config.set("plugins", "gdr", "gdrCHD.dll")
            Config.set("plugins", "gpu", "gpuDX11.dll")
            Config.set("plugins", "spu", "spuDemul.dll")
            Config.set("plugins", "pad", "padDemul.dll")
            Config.set("plugins", "net", "netDemul.dll")

            with open(configFileName, 'w', encoding='utf_8_sig') as configfile:
                Config.write(configfile)

        # adjust fullscreen & resolution to gpuDX11.ini
        configFileName = emupath + "/gpuDX11.ini"
        Config = configparser.ConfigParser(interpolation=None)
        Config.optionxform = str
        if os.path.exists(configFileName):
            try:
                with io.open(configFileName, 'r', encoding='utf_8_sig') as fp:
                    Config.readfp(fp)
            except:
                pass
        
        # set to be always fullscreen
        if not Config.has_section("main"):
            Config.add_section("main")
        Config.set("main","UseFullscreen", "1")
        # set resolution
        if not Config.has_section("resolution"):
            Config.add_section("resolution")
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

        #padDemul.ini

        # -run=<name>		run specified system (dc, naomi, awave, hikaru, gaelco, cave3rd)
        # -rom=<romname>	run specified system rom from the rom path defined in Demul.ini
        
        if "naomi2" in rom:
            demulsystem = "naomi"
        elif "hikaru" in rom:
            demulsystem = "hikaru"
        elif "gaelco" in rom:
            demulsystem = "gaelco"
        elif "cave3rd" in rom:
            demulsystem = "cave3ed"
        
        # now run the emulator
        commandArray = ["/usr/wine/proton/bin/wine", "explorer", "/desktop=Wine,{}x{}".format(gameResolution["width"], gameResolution["height"]), "/userdata/saves/demul/demul/demul.exe"]
        # other options tbd - hard coded for naomi for now
        commandArray.extend(["-run={}".format(demulsystem)])
        # now simplify the rom name
        if demulsystem == "naomi":
            romname = rom.replace("/userdata/roms/naomi2/", "")
        elif demulsystem == "hikaru":
            romname = rom.replace("/userdata/roms/hikaru/", "")
        elif demulsystem == "gaelco":
            romname = rom.replace("/userdata/roms/gaelco/", "")
        elif demulsystem == "cave3rd":
            romname = rom.replace("/userdata/roms/cave3rd/", "")
        
        smplromname = romname.replace(".zip", "")
        commandArray.extend(["-rom={}".format(smplromname)])

        return Command.Command(
            array=commandArray,
            env={
                "WINEPREFIX": wineprefix,
                "LD_LIBRARY_PATH": "/lib32:/usr/wine/proton/lib/wine",
                "LIBGL_DRIVERS_PATH": "/lib32/dri",
                # hum pw 0.2 and 0.3 are hardcoded, not nice
                "SPA_PLUGIN_DIR": "/usr/lib/spa-0.2:/lib32/spa-0.2",
                "PIPEWIRE_MODULE_DIR": "/usr/lib/pipewire-0.3:/lib32/pipewire-0.3"
            })
