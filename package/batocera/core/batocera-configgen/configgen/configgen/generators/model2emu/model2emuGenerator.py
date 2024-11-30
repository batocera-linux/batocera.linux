from __future__ import annotations

import filecmp
import logging
import os
import shutil
import stat
import subprocess
from pathlib import Path, PureWindowsPath
from typing import TYPE_CHECKING, Final

from ... import Command, controllersConfig
from ...batoceraPaths import HOME, ROMS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ...utils.configparser import CaseSensitiveConfigParser
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


eslog = logging.getLogger(__name__)

MODEL2_ROMS: Final = ROMS / "model2"

class Model2EmuGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "model2emu",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        wineprefix = HOME / "wine-bottles" / "model2"
        emupath = wineprefix / "model2emu"

        mkdir_if_not_exists(wineprefix)

        #copy model2emu to /userdata for rw & emulator directory creation reasons
        if not emupath.exists():
            shutil.copytree("/usr/model2emu", emupath)
            (emupath / "EMULATOR.INI").chmod(stat.S_IRWXO)

        # install windows libraries required
        d3dx9_done = wineprefix / "d3dx9.done"
        if not d3dx9_done.exists():
            cmd = ["/usr/wine/winetricks", "-q", "d3dx9"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/wine-tkg/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/wine-tkg/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with d3dx9_done.open("w") as f:
                f.write("done")

        d3dcompiler_42_done = wineprefix / "d3dcompiler_42.done"
        if not d3dcompiler_42_done.exists():
            cmd = ["/usr/wine/winetricks", "-q", "d3dcompiler_42"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/wine-tkg/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/wine-tkg/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with d3dcompiler_42_done.open("w") as f:
                f.write("done")

        d3dx9_42_done = wineprefix / "d3dx9_42.done"
        if not d3dx9_42_done.exists():
            cmd = ["/usr/wine/winetricks", "-q", "d3dx9_42"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/wine-tkg/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/wine-tkg/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with d3dx9_42_done.open("w") as f:
                f.write("done")

        xact_done = wineprefix / "xact.done"
        if not xact_done.exists():
            cmd = ["/usr/wine/winetricks", "-q", "xact"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/wine-tkg/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/wine-tkg/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with xact_done.open("w") as f:
                f.write("done")

        xact_x64_done = wineprefix / "xact_x64.done"
        if not xact_x64_done.exists():
            cmd = ["/usr/wine/winetricks", "-q", "xact_x64"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/wine-tkg/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/wine-tkg/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with xact_x64_done.open("w") as f:
                f.write("done")

        # for existing bottles we want to ensure files are updated as necessary
        copy_updated_files(Path("/usr/model2emu/scripts"), emupath / "scripts")

        xinput_cfg_done = wineprefix / "xinput_cfg.done"
        if not xinput_cfg_done.exists():
            copy_updated_files(Path("/usr/model2emu/CFG"), emupath / "CFG")
            with xinput_cfg_done.open("w") as f:
                f.write("done")

        # move to the emulator path to ensure configs are saved etc
        os.chdir(emupath)

        commandArray = ["/usr/wine/wine-tkg/bin/wine", emupath / "emulator_multicpu.exe"]
        # simplify the rom name (strip the directory & extension)
        if rom != 'config':
            rom = Path(rom).stem
            commandArray.extend([rom])

        # modify the ini file resolution accordingly
        configFileName = emupath / "EMULATOR.INI"
        Config = CaseSensitiveConfigParser(interpolation=None)
        if configFileName.is_file():
            Config.read(configFileName)

        # add subdirectories
        dirnum = 1 # existing rom path
        for possibledir in MODEL2_ROMS.iterdir():
            if possibledir.is_dir() and possibledir.name != "images":
                dirnum = dirnum + 1
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
        lua_file_path = emupath / "scripts" / f"{rom}.lua"
        if system.isOptSet("model2_ratio"):
            if lua_file_path.exists():
                modify_lua_widescreen(lua_file_path, system.config["model2_ratio"])
        else:
            if lua_file_path.exists():
                modify_lua_widescreen(lua_file_path, "False")
        # scanlines
        if system.isOptSet("model2_scanlines"):
            if lua_file_path.exists():
                modify_lua_scanlines(lua_file_path, system.config["model2_scanlines"])
        else:
            if lua_file_path.exists():
                modify_lua_scanlines(lua_file_path, "False")
        # sinden - check if rom is a gun game
        known_gun_roms = ["bel", "gunblade", "hotd", "rchase2", "vcop", "vcop2", "vcopa"]
        if rom in known_gun_roms:
            if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) > 0:
                for gun in guns:
                    if guns[gun]["need_borders"]:
                        if lua_file_path.exists():
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

        # xinput
        if system.isOptSet("model2_xinput") and system.getOptBoolean("model2_xinput"):
            Config.set("Input","XInput", "1")
        else:
            Config.set("Input","XInput", "0")

        # force feedback
        if system.isOptSet("model2_forceFeedback") and system.getOptBoolean("model2_forceFeedback"):
            Config.set("Input","EnableFF", "1")
        else:
            Config.set("Input","EnableFF", "0")

        with configFileName.open('w') as configfile:
            Config.write(configfile)

        # set the environment variables
        environment = {
            "WINEPREFIX": wineprefix,
            "LD_LIBRARY_PATH": "/lib32:/usr/wine/wine-tkg/lib/wine",
            "LIBGL_DRIVERS_PATH": "/lib32/dri",
            "SPA_PLUGIN_DIR": "/usr/lib/spa-0.2:/lib32/spa-0.2",
            "PIPEWIRE_MODULE_DIR": "/usr/lib/pipewire-0.3:/lib32/pipewire-0.3",
            "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
            "SDL_JOYSTICK_HIDAPI": "0"
        }

        # check if software render option is chosen
        if system.isOptSet("model2_Software") and system.config["model2_Software"] == "1":
            environment.update({
                "__GLX_VENDOR_LIBRARY_NAME": "mesa",
                "MESA_LOADER_DRIVER_OVERRIDE": "llvmpipe",
                "GALLIUM_DRIVER": "llvmpipe"
            })

        # ensure nvidia driver used for vulkan
        if Path('/var/tmp/nvidia.prime').exists():
            variables_to_remove = ['__NV_PRIME_RENDER_OFFLOAD', '__VK_LAYER_NV_optimus', '__GLX_VENDOR_LIBRARY_NAME']
            for variable_name in variables_to_remove:
                if variable_name in os.environ:
                    del os.environ[variable_name]

            environment.update(
                {
                    'VK_ICD_FILENAMES': '/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json',
                    'VK_LAYER_PATH': '/usr/share/vulkan/explicit_layer.d'
                }
            )

        # now run the emulator
        return Command.Command(array=commandArray, env=environment)


def modify_lua_widescreen(file_path: Path, condition: str) -> None:
    with file_path.open('r') as lua_file:
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

    with file_path.open('w') as lua_file:
        lua_file.writelines(modified_lines)

def modify_lua_scanlines(file_path: Path, condition: str) -> None:
    with file_path.open('r') as lua_file:
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

    with file_path.open('w') as lua_file:
        lua_file.writelines(modified_lines)

def modify_lua_sinden(file_path: Path, condition: str, thickness: str) -> None:
    with file_path.open('r') as lua_file:
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

    with file_path.open('w') as lua_file:
        lua_file.writelines(modified_lines)

def copy_updated_files(source_path: Path, destination_path: Path) -> None:
    dcmp = filecmp.dircmp(source_path, destination_path)

    # Copy missing files and files needing updates from source to destination
    for name in dcmp.left_only + dcmp.diff_files:
        src = source_path / name
        dst = destination_path / name

        if src.is_dir():
            shutil.copytree(src, dst)
            eslog.debug(f"Copying directory {src} to {dst}")
        else:
            shutil.copy2(src, dst)
            eslog.debug(f"Copying file {src} to {dst}")
