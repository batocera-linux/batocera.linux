#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
import batoceraFiles

ryujinxHome = batoceraFiles.CONF

class RyujinxGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        #commandArray = ["/usr/ryujinx/Ryujinx", rom ]
        return Command.Command(
            array=commandArray,
            env={"XDG_CONFIG_HOME":ryujinxHome, "XDG_DATA_HOME":ryujinxHome, "XDG_CACHE_HOME":batoceraFiles.CACHE, "QT_QPA_PLATFORM":"xcb"}
            )
