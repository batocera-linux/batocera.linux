#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
import batoceraFiles # GLOBAL VARIABLES

class YuzuGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):

        if not os.path.exists(batoceraFiles.CONF+"/yuzu"):
            os.makedirs(batoceraFiles.CONF+"/yuzu")

        commandArray = ["/usr/bin/yuzu", "-f", "-g", rom ]
        return Command.Command(array=commandArray, env={
            "XDG_CONFIG_HOME":batoceraFiles.CONF, \
            "XDG_DATA_HOME":batoceraFiles.SAVES + "/switch", \
            "XDG_CACHE_HOME":batoceraFiles.CACHE, \
            "QT_QPA_PLATFORM":"xcb"})
