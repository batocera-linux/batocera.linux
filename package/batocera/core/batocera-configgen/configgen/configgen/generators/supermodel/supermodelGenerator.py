from __future__ import annotations

import re
import shutil
from pathlib import Path
from shutil import copyfile
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import CONFIGS, SAVES, ensure_parents_and_open, mkdir_if_not_exists
from ...controller import Controller, generate_sdl_game_controller_config
from ...exceptions import BatoceraException
from ...gun import Guns, guns_need_crosses
from ...utils.configparser import CaseSensitiveConfigParser
from ..Generator import Generator

if TYPE_CHECKING:
    from ...controller import Controllers
    from ...Emulator import Emulator
    from ...types import HotkeysContext


SUPERMODEL_SHARE: Final = Path('/usr/share/supermodel')
SUPERMODEL_CONFIG: Final = CONFIGS / 'supermodel'
SUPERMODEL_SAVES: Final = SAVES / 'supermodel'


class SupermodelGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "supermodel",
            "keys": { "exit": "KEY_ESC", "menu": ["KEY_LEFTALT", "KEY_P"], "pause": ["KEY_LEFTALT", "KEY_P"], "reset": ["KEY_LEFTALT", "KEY_R"],
                      "save_state": "KEY_F5", "restore_state": "KEY_F7", "next_state": "KEY_F6"
                     }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray: list[str | Path] = ["supermodel", "-fullscreen", "-channels=2"]

        # legacy3d
        if system.config.get("engine3D") == "new3d":
            commandArray.append("-new3d")
        else:
            commandArray.extend(["-multi-texture", "-legacy-scsp", "-legacy3d"])

        # widescreen
        if system.config.get_bool("m3_wideScreen"):
            commandArray.append("-wide-screen")
            commandArray.append("-wide-bg")
            system.config["bezel"] == "none"

        # quad rendering
        if system.config.get_bool("quadRendering"):
            commandArray.append("-quad-rendering")

        # crosshairs
        if crosshairs := system.config.get("crosshairs"):
            commandArray.append(f"-crosshairs={crosshairs}")
        else:
            if guns_need_crosses(guns):
                if len(guns) == 1:
                    commandArray.append("-crosshairs=1")
                else:
                    commandArray.append("-crosshairs=3")

        # force feedback
        if system.config.get_bool("forceFeedback"):
            commandArray.append("-force-feedback")

        # powerpc frequesncy
        if freq := system.config.get("ppcFreq"):
            commandArray.append(f"-ppc-frequency={freq}")

        # crt colour
        if color := system.config.get("crt_colour"):
            commandArray.append(f"-crtcolors={color}")

        # upscale mode
        if upscale_mode := system.config.get("upscale_mode"):
            commandArray.append(f"-upscalemode={upscale_mode}")

        # resolution
        commandArray.append(f"-res={gameResolution['width']},{gameResolution['height']}")

        # logs
        commandArray.extend(["-log-output=/userdata/system/logs/Supermodel.log", rom])

        # copy nvram files
        copy_nvram_files()

        # copy gun asset files
        copy_asset_files()

        # copy xml
        copy_xml()

        # controller config
        configPadsIni(system, rom, guns)

        return Command.Command(
            array=commandArray,
            env={
                "SDL_VIDEODRIVER": "x11",
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if config.get('m3_wideScreen') == "1":
            return 16 / 9
        return 4 / 3

def copy_nvram_files():
    sourceDir = SUPERMODEL_SHARE / "NVRAM"
    targetDir = SUPERMODEL_SAVES / "NVRAM"

    mkdir_if_not_exists(targetDir)

    # create nv files which are in source and have a newer modification time than in target
    for sourceFile in sourceDir.iterdir():
        if sourceFile.suffix == ".nv":
            targetFile = targetDir / sourceFile.name
            if not targetFile.exists():
                # if the target file doesn't exist, just copy the source file
                copyfile(sourceFile, targetFile)
            else:
                # if the target file exists and has an older modification time than the source file, create a backup and copy the new file
                if sourceFile.stat().st_mtime > targetFile.stat().st_mtime:
                    backupFile = targetFile.with_suffix(f"{targetFile.suffix}.bak")
                    if backupFile.exists():
                        backupFile.unlink()
                    targetFile.rename(backupFile)
                    copyfile(sourceFile, targetFile)

def copy_asset_files():
    sourceDir = SUPERMODEL_SHARE / "Assets"
    targetDir = SUPERMODEL_CONFIG / "Assets"
    if not sourceDir.exists():
        return
    mkdir_if_not_exists(targetDir)

    # create asset files which are in source and have a newer modification time than in target
    for sourceFile in sourceDir.iterdir():
        targetFile = targetDir / sourceFile.name
        if not targetFile.exists() or sourceFile.stat().st_mtime > targetFile.stat().st_mtime:
            copyfile(sourceFile, targetFile)

def copy_xml():
    source_path = SUPERMODEL_SHARE / 'Games.xml'
    dest_path = SUPERMODEL_CONFIG / 'Games.xml'
    mkdir_if_not_exists(dest_path.parent)
    if not dest_path.exists() or source_path.stat().st_mtime > dest_path.stat().st_mtime:
        shutil.copy2(source_path, dest_path)

def configPadsIni(system: Emulator, rom: Path, guns: Guns) -> None:

    templateFile = SUPERMODEL_SHARE / "Supermodel.ini.template"
    targetFile = SUPERMODEL_CONFIG / "Supermodel.ini"

    # --- custom_config option: skip .ini generation if it already exists ---
    custom_config = int(system.config.get("custom_config", 0))

    if custom_config == 1 and targetFile.exists():
        # Use the existing Supermodel.ini file as-is, do not copy or overwrite
        return
    # -----------------------------------------------------------------------

    # template
    templateConfig = CaseSensitiveConfigParser(interpolation=None)
    templateConfig.read(templateFile, encoding='utf_8_sig')

    # target
    targetConfig = CaseSensitiveConfigParser(interpolation=None)

    for section in templateConfig.sections():
        targetConfig.add_section(section)
        for key, value in templateConfig.items(section):
            targetConfig.set(section, key, value)


    # evdev for guns or sdlgamepad
    for section in targetConfig.sections():
        if section.strip() in [ "Global", rom.stem ]:
            # for an input sytem
            if section.strip() != "Global":
                targetConfig.set(section, "InputSystem", "to be defined")
            for key, _ in targetConfig.items(section):
                if key == "InputSystem":
                    if system.config.use_guns and guns:
                        targetConfig.set(section, key, "evdev")
                    else:
                        targetConfig.set(section, key, "sdlgamepad")



    # save the ini file
    with ensure_parents_and_open(targetFile, 'w') as configfile:
        targetConfig.write(configfile)
