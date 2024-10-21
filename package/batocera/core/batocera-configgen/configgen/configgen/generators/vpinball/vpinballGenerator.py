from __future__ import annotations

import configparser
import logging
import shutil
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ...utils.batoceraServices import batoceraServices
from ...utils.configparser import CaseSensitiveConfigParser
from ..Generator import Generator
from . import vpinballOptions, vpinballWindowing

if TYPE_CHECKING:
    from ...types import HotkeysContext


eslog = logging.getLogger(__name__)

class VPinballGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "vpinball",
            "keys": { "exit": "KEY_Q", "coin": "KEY_5", "menu": "KEY_ESC", "pause": "KEY_ESC" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # files
        vpinballConfigPath     = CONFIGS / "vpinball"
        vpinballConfigFile     = vpinballConfigPath  / "VPinballX.ini"
        vpinballLogFile        = vpinballConfigPath / "vpinball.log"
        vpinballPinmameIniPath = vpinballConfigPath / "pinmame" / "ini"

        # create vpinball config directory and default config file if they don't exist
        mkdir_if_not_exists(vpinballConfigPath)
        if not vpinballConfigFile.exists():
            shutil.copy("/usr/bin/vpinball/assets/Default_VPinballX.ini", vpinballConfigFile)
        mkdir_if_not_exists(vpinballPinmameIniPath)
        if vpinballLogFile.exists():
            vpinballLogFile.rename(vpinballLogFile.with_suffix(f"{vpinballLogFile.suffix}.1"))

        ## [ VPinballX.ini ] ##
        try:
            vpinballSettings = CaseSensitiveConfigParser(interpolation=None, allow_no_value=True)
            vpinballSettings.read(vpinballConfigFile)
        except configparser.DuplicateOptionError as e:
            eslog.debug(f"Error reading VPinballX.ini: {e}")
            eslog.debug(f"*** Using default VPinballX.ini file ***")
            shutil.copy("/usr/bin/vpinball/assets/Default_VPinballX.ini", vpinballConfigFile)
            vpinballSettings = CaseSensitiveConfigParser(interpolation=None, allow_no_value=True)
            vpinballSettings.read(vpinballConfigFile)

        # init sections
        if not vpinballSettings.has_section("Standalone"):
            vpinballSettings.add_section("Standalone")
        if not vpinballSettings.has_section("Player"):
            vpinballSettings.add_section("Player")
        if not vpinballSettings.has_section("TableOverride"):
            vpinballSettings.add_section("TableOverride")

        # options
        vpinballOptions.configureOptions(vpinballSettings, system)

        # dmd
        hasDmd = (batoceraServices.getServiceStatus("dmd_real") == "started")

        # windows
        vpinballWindowing.configureWindowing(vpinballSettings, system, gameResolution, hasDmd)

        # DMDServer
        if hasDmd:
            vpinballSettings.set("Standalone", "DMDServer","1")
        else:
            vpinballSettings.set("Standalone", "DMDServer","0")

        # Save VPinballX.ini
        with vpinballConfigFile.open('w') as configfile:
            vpinballSettings.write(configfile)

        # set the config path to be sure
        commandArray = [
            "/usr/bin/vpinball/VPinballX_GL",
            "-PrefPath", vpinballConfigPath,
            "-Ini", vpinballConfigFile,
            "-Play", rom
        ]

        # SDL_RENDER_VSYNC is causing perf issues (set by emulatorlauncher.py)
        return Command.Command(array=commandArray, env={"SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers), "SDL_RENDER_VSYNC": "0"})

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
