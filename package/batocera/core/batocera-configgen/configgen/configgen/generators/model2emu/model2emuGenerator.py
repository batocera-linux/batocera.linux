from __future__ import annotations

import filecmp
import logging
import os
import shutil
import stat
from pathlib import Path, PureWindowsPath
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import HOME, ROMS, configure_emulator, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ...utils import wine
from ...utils.configparser import CaseSensitiveConfigParser
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


_logger = logging.getLogger(__name__)

MODEL2_ROMS: Final = ROMS / "model2"

class Model2EmuGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "model2emu",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, esmetadata, guns, wheels, gameResolution):
        wineprefix = HOME / "wine-bottles" / "model2"
        emupath = wineprefix / "model2emu"

        mkdir_if_not_exists(wineprefix)

        #copy model2emu to /userdata for rw & emulator directory creation reasons
        if not emupath.exists():
            shutil.copytree("/usr/model2emu", emupath)
            (emupath / "EMULATOR.INI").chmod(stat.S_IRWXO)

        # install windows libraries required
        wine.install_wine_trick(wineprefix, 'd3dx9')
        wine.install_wine_trick(wineprefix, 'd3dcompiler_42')
        wine.install_wine_trick(wineprefix, 'd3dx9_42')
        wine.install_wine_trick(wineprefix, 'xact')
        wine.install_wine_trick(wineprefix, 'xact_x64')

        # for existing bottles we want to ensure files are updated as necessary
        copy_updated_files(Path("/usr/model2emu/scripts"), emupath / "scripts")

        xinput_cfg_done = wineprefix / "xinput_cfg.done"
        if not xinput_cfg_done.exists():
            copy_updated_files(Path("/usr/model2emu/CFG"), emupath / "CFG")
            with xinput_cfg_done.open("w") as f:
                f.write("done")

        # move to the emulator path to ensure configs are saved etc
        os.chdir(emupath)

        commandArray: list[str | Path] = [wine.WINE, emupath / "emulator_multicpu.exe"]
        # simplify the rom name (strip the directory & extension)
        if not configure_emulator(rom):
            commandArray.extend([rom.stem])

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
        Config.set("Renderer","FullMode", system.config.get("model2_renderRes", "4"))
        Config.set("Renderer","AutoFull", "1")
        Config.set("Renderer","ForceSync", "1")
        # widescreen
        lua_file_path = emupath / "scripts" / f"{rom.stem}.lua"
        if lua_file_path.exists():
            modify_lua_widescreen(lua_file_path, system.config.get_bool("model2_ratio"))
        # scanlines
        if lua_file_path.exists():
            modify_lua_scanlines(lua_file_path, system.config.get_bool("model2_scanlines"))
        # sinden - check if rom is a gun game
        known_gun_roms = ["bel", "gunblade", "hotd", "rchase2", "vcop", "vcop2", "vcopa"]
        if rom.stem in known_gun_roms and system.config.use_guns and guns:
            for gun in guns:
                if gun.needs_borders:
                    if lua_file_path.exists():
                        bordersSize = system.guns_borders_size_name(guns)
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
        Config.set("Renderer","FakeGouraud", system.config.get("model2_fakeGouraud", "0"))
        Config.set("Renderer","Bilinear", system.config.get("model2_bilinearFiltering", "1"))
        Config.set("Renderer","Trilinear", system.config.get("model2_trilinearFiltering", "0"))
        Config.set("Renderer","FilterTilemaps", system.config.get("model2_filterTilemaps", "0"))
        Config.set("Renderer","ForceManaged", system.config.get("model2_forceManaged", "0"))
        Config.set("Renderer","AutoMip", system.config.get("model2_enableMIP", "0"))
        Config.set("Renderer","MeshTransparency", system.config.get("model2_meshTransparency", "0"))
        Config.set("Renderer","FSAA", system.config.get("model2_fullscreenAA", "0"))
        Config.set("Input","UseRawInput", system.config.get("model2_useRawInput", "0"))
        if crosshairs := system.config.get("model2_crossHairs"):
            Config.set("Renderer","DrawCross", crosshairs)
        else:
            for gun in guns:
                if gun.needs_cross:
                    Config.set("Renderer","DrawCross", "1")
                else:
                    Config.set("Renderer","DrawCross", "0")

        # xinput
        Config.set("Input","XInput", system.config.get_bool("model2_xinput", return_values=("1", "0")))

        # force feedback
        Config.set("Input","EnableFF", system.config.get_bool("model2_forceFeedback", return_values=("1", "0")))

        with configFileName.open('w') as configfile:
            Config.write(configfile)

        # set the environment variables
        environment = wine.get_wine_environment(wineprefix)
        environment.update({
            "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
            "SDL_JOYSTICK_HIDAPI": "0"
        })

        # check if software render option is chosen
        if system.config.get("model2_Software") == "1":
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


def modify_lua_widescreen(file_path: Path, condition: bool) -> None:
    with file_path.open('r') as lua_file:
        lines = lua_file.readlines()

    modified_lines: list[str] = []
    for line in lines:
        if condition:
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

def modify_lua_scanlines(file_path: Path, condition: bool) -> None:
    with file_path.open('r') as lua_file:
        original_lines = lua_file.readlines()

    modified_lines: list[str] = []
    scanlines_line_added = False

    for line in original_lines:
        if "TestSurface = Video_CreateSurfaceFromFile" in line:
            modified_lines.append(line)
            if "Options.scanlines.value=" not in line and not scanlines_line_added:
                modified_lines.append(f'\tOptions.scanlines.value={"1" if condition else "0"}\r\n')
                scanlines_line_added = True
        elif "Options.scanlines.value=" in line:
            if condition:
                modified_lines.append(line.replace("Options.scanlines.value=0", "Options.scanlines.value=1"))
            else:
                modified_lines.append(line.replace("Options.scanlines.value=1", "Options.scanlines.value=0"))
        else:
            modified_lines.append(line)

    with file_path.open('w') as lua_file:
        lua_file.writelines(modified_lines)

def modify_lua_sinden(file_path: Path, condition: str, thickness: str) -> None:
    with file_path.open('r') as lua_file:
        original_lines = lua_file.readlines()

    modified_lines: list[str] = []
    sinden_line_added = False

    for line in original_lines:
        if "TestSurface = Video_CreateSurfaceFromFile" in line:
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
            _logger.debug("Copying directory %s to %s", src, dst)
        else:
            shutil.copy2(src, dst)
            _logger.debug("Copying file %s to %s", src, dst)
