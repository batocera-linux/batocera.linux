#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import os.path
from os.path import dirname
from os.path import isdir
from os.path import isfile
import glob
import ConfigParser

class DosBoxxGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        # Find rom path
        gameDir = rom
        batFile = gameDir + "/dosbox.bat"
        gameConfFile = gameDir + "/dosbox.cfg"

        configFile = batoceraFiles.dosboxxConfig
        if os.path.isfile(gameConfFile):
            configFile = gameConfFile

        # configuration file
        iniSettings = ConfigParser.ConfigParser()
        # To prevent ConfigParser from converting to lower case
        iniSettings.optionxform = str
        if os.path.exists(configFile):
            iniSettings.read(configFile)

        # sections
        if not iniSettings.has_section("sdl"):
            iniSettings.add_section("sdl")
        iniSettings.set("sdl", "output", "opengl")

        # save
        with open(configFile, 'w') as config:
            iniSettings.write(config)

        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']],
			"-exit", 
			"-c", """mount c {}""".format(gameDir),
                        "-c", "c:",
                        "-c", "dosbox.bat",
                        "-fastbioslogo",
                        "-fullscreen",
                        "-conf {}".format(configFile)]

        return Command.Command(array=commandArray)
