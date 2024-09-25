import configparser
import os

from ... import Command
from ... import batoceraFiles
from ..Generator import Generator
from . import mupenConfig
from . import mupenControllers

class MupenGenerator(Generator):

    def getHotkeysContext(self):
        return {
            "name": "mupen64",
            "keys": { "exit": "KEY_ESC", "save_state": "KEY_F5", "restore_state": "KEY_F7", "menu": "KEY_P" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # Read the configuration file
        iniConfig = configparser.ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        iniConfig.optionxform = str
        if os.path.exists(batoceraFiles.mupenCustom):
            iniConfig.read(batoceraFiles.mupenCustom)
        else:
            if not os.path.exists(os.path.dirname(batoceraFiles.mupenCustom)):
                os.makedirs(os.path.dirname(batoceraFiles.mupenCustom))
            iniConfig.read(batoceraFiles.mupenCustom)

        mupenConfig.setMupenConfig(iniConfig, system, playersControllers, gameResolution)
        mupenControllers.setControllersConfig(iniConfig, playersControllers, system, wheels)

        # Save the ini file
        if not os.path.exists(os.path.dirname(batoceraFiles.mupenCustom)):
            os.makedirs(os.path.dirname(batoceraFiles.mupenCustom))
        with open(batoceraFiles.mupenCustom, 'w') as configfile:
            iniConfig.write(configfile)

        # Command
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "--corelib", "/usr/lib/libmupen64plus.so.2.0.0", "--gfx", "/usr/lib/mupen64plus/mupen64plus-video-{}.so".format(system.config['core']), "--configdir", batoceraFiles.mupenConf, "--datadir", batoceraFiles.mupenConf]

        # state_filename option
        if system.isOptSet('state_filename'):
            commandArray.extend(["--savestate", system.config['state_filename']])

        commandArray.append(rom)

        return Command.Command(array=commandArray)

    def getInGameRatio(self, config, gameResolution, rom):
        if ("mupen64plus_ratio" in config and config["mupen64plus_ratio"] == "16/9") or ("mupen64plus_ratio" not in config and "ratio" in config and config["ratio"] == "16/9"):
            return 16/9
        return 4/3
