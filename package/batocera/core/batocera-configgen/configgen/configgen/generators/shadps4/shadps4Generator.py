from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import toml

from ... import Command
from ...batoceraPaths import CONFIGS
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

eslog = logging.getLogger(__name__)

class shadPS4Generator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "shadps4",
            "keys": {"exit": ["KEY_LEFTALT", "KEY_F4"]}
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # Set the paths using Path objects
        configPath = Path(CONFIGS) / "shadps4"
        if rom != "config":
            romPath = Path(rom).parent / "eboot.bin"
        romDir = Path("/userdata/roms/ps4")
        dlcPath = romDir / "DLC"

        os.makedirs(configPath, exist_ok=True)

        # Check Vulkan first before doing anything
        discrete_index = 0
        try:
            have_vulkan = subprocess.check_output(["/usr/bin/batocera-vulkan", "hasVulkan"], text=True).strip()
            if have_vulkan == "true":
                eslog.debug("Vulkan driver is available on the system.")
                try:
                    vulkan_version = subprocess.check_output(["/usr/bin/batocera-vulkan", "vulkanVersion"], text=True).strip()
                    if vulkan_version > "1.3":
                        eslog.debug(f"Using Vulkan version: {vulkan_version}")
                        try:
                            have_discrete = subprocess.check_output(["/usr/bin/batocera-vulkan", "hasDiscrete"], text=True).strip()
                            if have_discrete == "true":
                                eslog.debug("A discrete GPU is available on the system. We will use that for performance")
                                try:
                                    discrete_index = subprocess.check_output(["/usr/bin/batocera-vulkan", "discreteIndex"], text=True).strip()
                                    if discrete_index != "":
                                        eslog.debug(f"Using Discrete GPU Index: {discrete_index} for shadPS4")
                                    else:
                                        eslog.debug("Couldn't get discrete GPU index")
                                except subprocess.CalledProcessError:
                                    eslog.debug("Error getting discrete GPU index")
                            else:
                                eslog.debug("Discrete GPU is not available on the system. Using default.")
                                discrete_index = 0
                        except subprocess.CalledProcessError:
                            eslog.debug("Error checking for discrete GPU.")
                    else:
                        eslog.debug(f"Vulkan version: {vulkan_version} is not compatible with shadPS4")
                except subprocess.CalledProcessError:
                    eslog.debug("Error checking for Vulkan version.")
            else:
                eslog.debug("*** Vulkan driver required is not available on the system!!! ***")
                sys.exit(1)
        except subprocess.CalledProcessError:
            eslog.debug("Error executing batocera-vulkan script.")

        # Adjust the config.toml file
        config = {}
        toml_file = configPath / "user" / "config.toml"

        # Check if the file exists
        if toml_file.is_file():
            with toml_file.open() as f:
                config = toml.load(f)
        else:
            config = {
                "Settings": {"consoleLanguage": 1},
                "GUI": {
                    "mw_width": 1920,
                    "gameTableMode": 0,
                    "theme": 0,
                    "geometry_y": 0,
                    "geometry_h": 1080,
                    "geometry_w": 1920,
                    "geometry_x": 0,
                    "addonInstallDir": str(dlcPath),
                    "pkgDirs": [],
                    "recentFiles": [],
                    "installDir": str(romDir),
                    "sliderPosGrid": 0,
                    "emulatorLanguage": "en",
                    "iconSize": 36,
                    "elfDirs": [],
                    "sliderPos": 0,
                    "iconSizeGrid": 69,
                    "mw_height": 1080
                },
                "Debug": {"DebugDump": False},
                "Vulkan": {
                    "crashDiagnostic": False,
                    "rdocEnable": False,
                    "validation_gpu": False,
                    "validation_sync": False,
                    "rdocMarkersEnable": False,
                    "validation": False,
                    "gpuId": int(discrete_index)
                },
                "GPU": {
                    "dumpShaders": False,
                    "vblankDivider": 1,
                    "copyGPUBuffers": False,
                    "nullGpu": False,
                    "screenHeight": 720,
                    "screenWidth": 1280
                },
                "Input": {
                    "specialPadClass": 1,
                    "useSpecialPad": False,
                    "cursorHideTimeout": 5,
                    "cursorState": 1
                },
                "General": {
                    "backButtonBehavior": "left",
                    "showSplash": False,
                    "autoUpdate": False,
                    "userName": "Batocera",
                    "logType": "sync",
                    "BGMvolume": 50,
                    "playBGM": False,
                    "updateChannel": "",
                    "logFilter": "",
                    "Fullscreen": True,
                    "isPS4Pro": False
                }
            }

        # If the file exists, update the relevant sections
        config.setdefault("General", {})["Fullscreen"] = True
        config["General"]["autoUpdate"] = False
        config["General"]["userName"] = "Batocera"
        config.setdefault("GUI", {})["installDir"] = str(romDir)
        config["GUI"]["addonInstallDir"] = str(dlcPath)
        config.setdefault("Vulkan", {})["gpuId"] = int(discrete_index)

        # Create necessary directories if they do not exist
        os.makedirs(toml_file.parent, exist_ok=True)

        # Now write the updated toml
        with toml_file.open("w") as f:
            toml.dump(config, f)

        # Change to the configPath directory before running
        os.chdir(configPath)

        # Run command
        if rom == "config":
            commandArray: list[str | Path] = ["/usr/bin/shadps4/shadps4"]
        else:
            commandArray: list[str | Path] = ["/usr/bin/shadps4/shadps4", str(romPath)]

        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9
