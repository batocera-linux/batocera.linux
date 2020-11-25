#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import os.path, shutil
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

        # copy config file to custom config file to avoid overwritting by dosbox-x
        customConfFile = os.path.join(batoceraFiles.dosboxxCustom,'dosboxx-custom.conf')

        if os.path.exists(configFile):
            shutil.copy2(configFile, customConfFile)
            iniSettings.read(customConfFile)

        # sections
        if not iniSettings.has_section("sdl"):
            iniSettings.add_section("sdl")
        iniSettings.set("sdl", "output", "opengl")

        # save
        with open(customConfFile, 'w') as config:
            iniSettings.write(config)

        # -fullscreen removed as it crashes on N2
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']],
			"-exit", 
			"-c", """mount c {}""".format(gameDir),
                        "-c", "c:",
                        "-c", "dosbox.bat",
                        "-fastbioslogo",
                        "-conf {}".format(customConfFile)]

        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF})
