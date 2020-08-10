#!/usr/bin/env python

from generators.Generator import Generator
import batoceraFiles
import Command
import shutil
import os
from utils.logger import eslog
from os import path
from os import environ
import ConfigParser

class Rpcs3Generator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        romBasename = path.basename(rom)
        romName = rom + '/PS3_GAME/USRDIR/EBOOT.BIN'
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], romName]
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_CACHE_HOME":batoceraFiles.SAVES, "QT_QPA_PLATFORM":"xcb"})