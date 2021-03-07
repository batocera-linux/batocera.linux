#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import xemuConfig
import shutil
import os.path
import ConfigParser
# TODO: python3 - delete me!
import codecs
import controllersConfig

class XemuGenerator(Generator):

    # Main entry of the module
    # Configure fba and return a command
    def generate(self, system, rom, playersControllers, gameResolution):
        xemuConfig.writeIniFile(system, rom, playersControllers)

        # the command to run
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']]]
        commandArray.append("-config_path")
        commandArray.append(batoceraFiles.xemuConfig)

        env = {}
        env["XDG_CONFIG_HOME"] = batoceraFiles.CONF
        env["SDL_GAMECONTROLLERCONFIG"] = controllersConfig.generateSdlGameControllerConfig(playersControllers)

        return Command.Command(array=commandArray, env=env)
