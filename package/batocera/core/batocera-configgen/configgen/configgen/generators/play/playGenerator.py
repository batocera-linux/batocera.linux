#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import controllersConfig
import os
from os import path

playConfig = batoceraFiles.CONF + '/play'
playSaves = batoceraFiles.SAVES + '/play'
playHome = batoceraFiles.CONF

class PlayGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):

        # Create config folder
        if not path.isdir(playConfig):
            os.mkdir(playConfig)

        # Create save folder
        if not path.isdir(playSaves):
            os.mkdir(playSaves)

        commandArray = ["/usr/bin/play-emu", "--disc", rom]
        return Command.Command(
            array=commandArray,
            env={"XDG_CONFIG_HOME":playConfig, "XDG_DATA_HOME":playConfig, "XDG_CACHE_HOME":batoceraFiles.CACHE, "QT_QPA_PLATFORM":"xcb"}
            )

    def getMouseMode(self, config):
        return True
