#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Command
import batoceraFiles
import shutil
import os.path
from . import linappleConfig
import configparser
from shutil import copyfile
from os.path import dirname
from os.path import isdir
from os.path import isfile
from generators.Generator import Generator


class LinappleGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        
        # Master.dsk
        if not isfile(batoceraFiles.linappleMasterDSKFile):
            if not isdir(dirname(batoceraFiles.linappleConfigFile)):
                os.mkdir(dirname(batoceraFiles.linappleConfigFile))
            copyfile(batoceraFiles.linappleMasterDSK, batoceraFiles.linappleMasterDSKFile)

        # Configuration
        linappleConfig.generateLinappleConfig(rom, playersControllers, gameResolution)

        commandArray = [ batoceraFiles.batoceraBins[system.config['emulator']], "-f", "--autoboot" ]

        return Command.Command(array=commandArray)
