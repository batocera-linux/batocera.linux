#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import shutil
import os.path
import configparser
# TODO: python3 - delete me!
import codecs
import controllersConfig
from shutil import copyfile
from . import xemuConfig

class XemuGenerator(Generator):

    # Main entry of the module
    # Configure fba and return a command
    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
        xemuConfig.writeIniFile(system, rom, playersControllers, gameResolution)

        # copy the hdd if it doesn't exist
        if not os.path.exists("/userdata/saves/xbox/xbox_hdd.qcow2"):
            if not os.path.exists("/userdata/saves/xbox"):
                os.makedirs("/userdata/saves/xbox")
            copyfile("/usr/share/xemu/data/xbox_hdd.qcow2", "/userdata/saves/xbox/xbox_hdd.qcow2")

        # the command to run
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']]]
        commandArray.extend(["-config_path", batoceraFiles.xemuConfig])

        environment = {
            "XDG_CONFIG_HOME": batoceraFiles.CONF,
            "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)
        }

        return Command.Command(array=commandArray, env=environment)
    
    def getInGameRatio(self, config, gameResolution, rom):
        if ("xemu_scaling" in config and config["xemu_scaling"] == "stretch") or ("xemu_aspect" in config and config["xemu_aspect"] == "16x9"):
            return 16/9
        return 4/3
