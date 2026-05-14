#
# This file is part of the batocera distribution (https://batocera.org).
# Copyright (c) 2025+.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# YOU MUST KEEP THIS HEADER AS IT IS
#
from __future__ import annotations

import logging
import os
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import toml

from ... import Command
from ...batoceraPaths import CONFIGS, BIOS, configure_emulator, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ...utils import vulkan
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

_logger = logging.getLogger(__name__)

class shadPS4Generator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "shadps4",
            "keys": {"exit": ["KEY_LEFTALT", "KEY_F4"]}
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # Set the paths using Path objects
        configPath = CONFIGS / "shadps4"
        userConfigPath = configPath / "user"
        toml_file = userConfigPath / "config.toml"
        savesPath = Path("/userdata/saves/shadps4")
        romDir = Path("/userdata/roms/ps4")
        dlcPath = romDir / "DLC"
        sysmodulesPath = userConfigPath / "sys_modules"
        sysmodulesBiosPath = BIOS/ "ps4/sys_modules"

        mkdir_if_not_exists(userConfigPath)
        mkdir_if_not_exists(savesPath)

        #symlink bios sys_module
        if sysmodulesBiosPath.is_dir() and not sysmodulesPath.is_symlink():
            if sysmodulesPath.is_dir():
                shutil.rmtree(sysmodulesPath)

            sysmodulesPath.symlink_to(sysmodulesBiosPath, target_is_directory=True)

        # Check Vulkan first before doing anything
        discrete_index = -1
        if vulkan.is_available():
            _logger.debug("Vulkan driver is available on the system.")
            vulkan_version = vulkan.get_version()
            if vulkan_version > "1.3":
                _logger.debug("Using Vulkan version: %s", vulkan_version)
                if vulkan.has_discrete_gpu():
                    _logger.debug("A discrete GPU is available on the system. We will use that for performance")
                    discrete_index = vulkan.get_discrete_gpu_index()
                    if discrete_index:
                        _logger.debug("Using Discrete GPU Index: %s for shadPS4", discrete_index)
                    else:
                        _logger.debug("Couldn't get discrete GPU index")
                        discrete_index = 0
                else:
                    _logger.debug("Discrete GPU is not available on the system. Using default.")
            else:
                _logger.debug("Vulkan version: %s is not compatible with shadPS4", vulkan_version)
        else:
            _logger.debug("*** Vulkan driver required is not available on the system!!! ***")
            sys.exit(1)

        # Adjust the config.toml file
        config: dict[str, dict[str, object]] = {}

        # Check if the file exists
        if toml_file.is_file():
            try:
                with toml_file.open("r") as f:
                    config = toml.load(f)
            except Exception as e:
                 _logger.error("Failed to load existing shadps4 config: %s. Will create default.", e)

        # If config is empty, create default structure
        if not config:
             _logger.info("Creating default shadps4 config at %s", toml_file)
             config = {
                "General": {
                    "isPS4Pro": False,
                    "isTrophyPopupDisabled": False,
                    "trophyNotificationDuration": 6.0,
                    "playBGM": False,
                    "BGMvolume": 50,
                    "enableDiscordRPC": False,
                    "logFilter": "",
                    "logType": "async",
                    "userName": "Batocera",
                    "updateChannel": "Release",
                    "chooseHomeTab": "General",
                    "showSplash": False,
                    "autoUpdate": False,
                    "alwaysShowChangelog": False,
                    "sideTrophy": "right",
                    "separateUpdateEnabled": False,
                    "compatibilityEnabled": False,
                    "checkCompatibilityOnStartup": False,
                },
                "Input": {
                    "cursorState": 1,
                    "cursorHideTimeout": 5,
                    "backButtonBehavior": "left",
                    "useSpecialPad": False,
                    "specialPadClass": 1,
                    "isMotionControlsEnabled": True,
                    "useUnifiedInputConfig": True,
                },
                "GPU": {
                    "screenWidth": int(gameResolution["width"]),
                    "screenHeight": int(gameResolution["height"]),
                    "nullGpu": False,
                    "copyGPUBuffers": False,
                    "dumpShaders": False,
                    "patchShaders": True,
                    "vblankDivider": 1,
                    "Fullscreen": True,
                    "FullscreenMode": "Fullscreen (Borderless)",
                    "allowHDR": False,
                },
                "Vulkan": {
                    "gpuId": int(discrete_index),
                    "validation": False,
                    "validation_sync": False,
                    "validation_gpu": False,
                    "crashDiagnostic": False,
                    "hostMarkers": False,
                    "guestMarkers": False,
                    "rdocEnable": False,
                },
                "Debug": {
                    "DebugDump": False,
                    "CollectShader": False,
                    "isSeparateLogFilesEnabled": False,
                    "FPSColor": True,
                },
                "Keys": {
                    "TrophyKey": ""
                 },
                "GUI": {
                    "installDirs": [str(romDir)],
                    "saveDataPath": str(savesPath),
                    "loadGameSizeEnabled": True,
                    "addonInstallDir": str(dlcPath),
                    "emulatorLanguage": "en_US",
                    "backgroundImageOpacity": 50,
                    "showBackgroundImage": True,
                    "mw_width": int(gameResolution["width"]),
                    "mw_height": int(gameResolution["height"]),
                    "theme": 0,
                    "iconSize": 36,
                    "sliderPos": 0,
                    "iconSizeGrid": 69,
                    "sliderPosGrid": 0,
                    "gameTableMode": 0,
                    "geometry_x": 0,
                    "geometry_y": 0,
                    "geometry_w": int(gameResolution["width"]),
                    "geometry_h": int(gameResolution["height"]),
                    "pkgDirs": [str(romDir)],
                    "elfDirs": [],
                    "recentFiles": [],
                },
                "Settings": {
                    "consoleLanguage": 1
                },
             }

        # --- Apply Batocera Specific Overrides ---
        # General
        config.setdefault("General", {})["autoUpdate"] = False
        config.setdefault("General", {})["enableDiscordRPC"] = False
        config.setdefault("General", {})["userName"] = "Batocera"

        # GPU
        gpu_config = config.setdefault("GPU", {})
        gpu_config["Fullscreen"] = True
        gpu_config["FullscreenMode"] = "Fullscreen (Borderless)"
        gpu_config["screenWidth"] = int(gameResolution["width"])
        gpu_config["screenHeight"] = int(gameResolution["height"])

        # GUI
        gui_config = config.setdefault("GUI", {})
        gui_config["addonInstallDir"] = str(dlcPath)
        gui_config["installDirs"] = [str(romDir)]
        gui_config["saveDataPath"] = str(savesPath)
        gui_config["mw_width"] = int(gameResolution["width"])
        gui_config["mw_height"] = int(gameResolution["height"])
        gui_config["geometry_w"] = int(gameResolution["width"])
        gui_config["geometry_h"] = int(gameResolution["height"])
        gui_config["pkgDirs"] = [str(romDir)]

        # Vulkan - Set the detected GPU ID
        config.setdefault("Vulkan", {})["gpuId"] = int(discrete_index)

        # Options
        if system.config.get_bool("shadps4_hdr"):
            gpu_config["allowHDR"] = True
        else:
            gpu_config["allowHDR"] = False
        if system.config.get("shadps4_console_lang"):
            config["Settings"]["consoleLanguage"] = int(system.config["shadps4_console_lang"])
        else:
            config["Settings"]["consoleLanguage"] = 1

        # Create necessary directories if they do not exist
        mkdir_if_not_exists(toml_file.parent)

        # Now write the updated toml
        with toml_file.open("w") as f:
            toml.dump(config, f)

        # Change to the configPath directory before running
        os.chdir(configPath)

        # Run command
        if configure_emulator(rom):
            commandArray: list[str | Path] = ["/usr/bin/shadps4/shadps4"]
        else:
            if rom.is_dir():
                commandArray: list[str | Path] = ["/usr/bin/shadps4/shadps4", rom / "eboot.bin"]
            else:
                commandArray: list[str | Path] = ["/usr/bin/shadps4/shadps4", rom.parent / "eboot.bin"]

        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9
