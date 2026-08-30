from __future__ import annotations

import configparser
import logging
from typing import TYPE_CHECKING

from batocera_common.configparser import CaseSensitiveConfigParser

from ... import Command
from ...batoceraPaths import CONFIGS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ...utils.batoceraServices import batoceraServices
from ..Generator import Generator
from . import vpinballOptions, vpinballWindowing

if TYPE_CHECKING:
    from ...types import HotkeysContext

_logger = logging.getLogger(__name__)

class VPinballGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "vpinball",
            "keys": { "exit": "KEY_ESC", "menu": "KEY_F12", "reset": "KEY_F3", "pause": "KEY_P", "coin": "KEY_5" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # files
        vpinballConfigPath         = CONFIGS / "vpinball"
        vpinballConfigFile         = vpinballConfigPath  / "VPinballX.ini"
        vpinballConfigFileOverride = vpinballConfigPath  / "VPinballX_override.ini"
        vpinballLogFile            = vpinballConfigPath / "vpinball.log"

        ## create vpinball config directory and a fresh config file if they don't exist
        mkdir_if_not_exists(vpinballConfigPath)
        if not vpinballConfigFile.exists():
            vpinballConfigFile.write_text("")
        if vpinballLogFile.exists():
            vpinballLogFile.rename(vpinballLogFile.with_suffix(f"{vpinballLogFile.suffix}.1"))

        ## [ VPinballX.ini ] ##
        try:
            vpinballSettings = CaseSensitiveConfigParser(interpolation=None, allow_no_value=True)
            vpinballSettings.read(vpinballConfigFile)
        except configparser.DuplicateOptionError as e:
            _logger.debug("Error reading VPinballX.ini: %s", e)
            _logger.debug("*** Recreating a fresh VPinballX.ini file ***")
            vpinballConfigFile.write_text("")
            vpinballSettings = CaseSensitiveConfigParser(interpolation=None, allow_no_value=True)
            vpinballSettings.read(vpinballConfigFile)

        # plugins to enable
        for plugin in ["Plugin.AltSound",
                       "Plugin.B2SLegacy",
                       "Plugin.DMDUtil",
                       "Plugin.FlexDMD",
                       "Plugin.PinMAME",
                       "Plugin.PUP",
                       "Plugin.ScoreView",
                       "Plugin.Serum",
                       "Plugin.WMP",
                       "Plugin.VNI",
                       "Plugin.vpx",
                       "Plugin.DOF",
                       "Plugin.Inspector"]:
            if not vpinballSettings.has_section(plugin):
                vpinballSettings.add_section(plugin)
            vpinballSettings.set(plugin, "Enable","1")

        # Altsound
        vpinballSettings.set("Plugin.AltSound", "Enable", system.config.get_bool("vpinball_altsound", True, return_values=("1", "0")))

        # DMDServer
        hasDmd = (batoceraServices.getServiceStatus("dmd_real") == "started")
        if hasDmd:
            vpinballSettings.set("Plugin.DMDUtil", "Enable","1")
            vpinballSettings.set("Plugin.DMDUtil", "DMDServer","1")
        else:
            vpinballSettings.set("Plugin.DMDUtil", "Enable","0")
            vpinballSettings.set("Plugin.DMDUtil", "DMDServer","0")

        # options
        vpinballOptions.configureOptions(vpinballSettings, system)

        # windows
        vpinballWindowing.configureWindowing(vpinballSettings, system, gameResolution, hasDmd)

        # Override values
        if vpinballConfigFileOverride.exists():
            try:
                _logger.debug("reading VPinballX_override.ini")
                vpinballSettingsOverride = CaseSensitiveConfigParser(interpolation=None, allow_no_value=True)
                vpinballSettingsOverride.read(vpinballConfigFileOverride)
                VPinballGenerator.overrideIniWith(vpinballSettings, vpinballSettingsOverride)
            except Exception as e:
                _logger.debug("Error reading VPinballX_override.ini: %s", e)
        else:
            _logger.debug("no VPinballX_override.ini found")

        # Save VPinballX.ini
        with vpinballConfigFile.open('w') as configfile:
            vpinballSettings.write(configfile)

        # set the config path to be sure
        commandArray = [
            "/usr/bin/vpinball/VPinballX_BGFX",
            "-PrefPath", vpinballConfigPath,
            "-Ini", vpinballConfigFile,
            "-Play", rom
        ]

        # SDL_RENDER_VSYNC is causing perf issues (set by emulatorlauncher.py)
        return Command.Command(array=commandArray, env={"SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers), "SDL_RENDER_VSYNC": "0"})

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9

    @staticmethod
    def overrideIniWith(vpinballSettings, vpinballSettingsOverride):
        for section in vpinballSettingsOverride.sections():
            if not vpinballSettings.has_section(section):
                vpinballSettings.add_section(section)
            for option, value in vpinballSettingsOverride.items(section):
                vpinballSettings.set(section, option, value)
                _logger.debug("Override value: [%s] %s = %s", section, option, value)
