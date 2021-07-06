#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import controllersConfig
import os
from os import path

ecwolfConfig  = batoceraFiles.CONF + "/ecwolf"
ecwolfSaves   = batoceraFiles.SAVES + "/ecwolf"

class ECWolfGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        # Create config folder
        if not path.isdir(ecwolfConfig):
            os.mkdir(ecwolfConfig)

        # Create save folder
        if not path.isdir(ecwolfSaves):
            os.mkdir(ecwolfSaves)

        os.chdir(rom)
        commandArray = ["/usr/share/ecwolf/ecwolf", "--fullscreen", "--joystick", "--savedir /userdata/saves/ecwolf", "--config /userdata/system/configs/ecwolf/ecwolf.cfg"]
        #commandArray = ["/usr/share/ecwolf/ecwolf", "--fullscreen", "--joystick", "--savedir /userdata/saves/ecwolf", rom]
        return Command.Command(
            array=commandArray)

    def getMouseMode(self, config):
        return True
