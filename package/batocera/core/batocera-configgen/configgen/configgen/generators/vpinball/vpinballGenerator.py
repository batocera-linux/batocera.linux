#!/usr/bin/env python

import os
import configparser
import Command
from generators.Generator import Generator
import batoceraFiles
import shutil
from utils.logger import get_logger
import controllersConfig
from utils.batoceraServices import batoceraServices
from . import vpinballWindowing
from . import vpinballOptions

eslog = get_logger(__name__)

class VPinballGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # files
        vpinballConfigPath     = batoceraFiles.CONF + "/vpinball"
        vpinballConfigFile     = vpinballConfigPath + "/VPinballX.ini"
        vpinballLogFile        = vpinballConfigPath + "/vpinball.log"
        vpinballPinmameIniPath = batoceraFiles.CONF + "/vpinball/pinmame/ini"

        # create vpinball config directory and default config file if they don't exist
        if not os.path.exists(vpinballConfigPath):
            os.makedirs(vpinballConfigPath)
        if not os.path.exists(vpinballConfigFile):
            shutil.copy("/usr/bin/vpinball/assets/Default_VPinballX.ini", vpinballConfigFile)
        if not os.path.exists(vpinballPinmameIniPath):
            os.makedirs(vpinballPinmameIniPath)
        if os.path.exists(vpinballLogFile):
            os.rename(vpinballLogFile, vpinballLogFile + ".1")

        ## [ VPinballX.ini ] ##
        try:
            vpinballSettings = configparser.ConfigParser(interpolation=None, allow_no_value=True)
            vpinballSettings.optionxform = str
            vpinballSettings.read(vpinballConfigFile)
        except configparser.DuplicateOptionError as e:
            eslog.debug(f"Error reading VPinballX.ini: {e}")
            eslog.debug(f"*** Using default VPinballX.ini file ***")
            shutil.copy("/usr/bin/vpinball/assets/Default_VPinballX.ini", vpinballConfigFile)
            vpinballSettings = configparser.ConfigParser(interpolation=None, allow_no_value=True)
            vpinballSettings.optionxform = str
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
        with open(vpinballConfigFile, 'w') as configfile:
            vpinballSettings.write(configfile)

        # set the config path to be sure
        commandArray = [
            "/usr/bin/vpinball/VPinballX_GL",
            "-PrefPath", vpinballConfigPath,
            "-Ini", vpinballConfigFile,
            "-Play", rom
        ]

        # SDL_RENDER_VSYNC is causing perf issues (set by emulatorlauncher.py)
        return Command.Command(array=commandArray, env={"SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers), "SDL_RENDER_VSYNC": "0"})

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
