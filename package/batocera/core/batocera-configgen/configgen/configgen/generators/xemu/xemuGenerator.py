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

class XemuGenerator(Generator):

    # Main entry of the module
    # Configure fba and return a command
    def generate(self, system, rom, playersControllers, gameResolution):
        xemuConfig.writeIniFile(system, rom)

        # the command to run
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']]]
        commandArray.append("-config_path")
        commandArray.append(batoceraFiles.xemuConfig)
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF})
