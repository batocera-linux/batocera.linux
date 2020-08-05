#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
from os import path

class Rpcs3Generator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        romBasename = path.basename(rom)

        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], rom]
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_CACHE_HOME":batoceraFiles.SAVES, "QT_QPA_PLATFORM":"xcb"})