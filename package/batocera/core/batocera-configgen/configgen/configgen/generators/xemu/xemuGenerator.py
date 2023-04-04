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
    def generate(self, system, rom, playersControllers, guns, gameResolution):
        xemuConfig.writeIniFile(system, rom, playersControllers)

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

        # check if the Zink render option is chosen
        if system.isOptSet("use_zink") and system.config["use_zink"] == "true":
            environment = {
                "XDG_CONFIG_HOME": batoceraFiles.CONF,
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers),
                "__GLX_VENDOR_LIBRARY_NAME": "mesa",
                "MESA_LOADER_DRIVER_OVERRIDE": "zink",
                "GALLIUM_DRIVER": "zink"
            }

        return Command.Command(array=commandArray, env=environment)
