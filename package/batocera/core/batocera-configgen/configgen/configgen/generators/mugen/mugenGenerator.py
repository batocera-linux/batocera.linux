#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
import controllersConfig
import configparser
import re

class MugenGenerator(Generator):

    @staticmethod
    def cleanMugenCfg(path):
        with open(path, 'r') as f:
            contents = f.read()

        contents = re.sub(r'^[ ]*;', ';', contents, 0, re.MULTILINE)
        with open(path, 'w') as f:
            f.write(contents)

    def generate(self, system, rom, playersControllers, gameResolution):

        settings = configparser.ConfigParser(interpolation=None, strict=False) # strict=False to allow to read duplicates set by users
        # To prevent ConfigParser from converting to lower case
        settings.optionxform = str
        settings_path = rom + "/data/mugen.cfg"
        if os.path.exists(settings_path):
            MugenGenerator.cleanMugenCfg(settings_path)
            settings.read(settings_path)

        if not settings.has_section("Video"):
            settings.add_section("Video")
        settings.set("Video", "FullScreen", "1")
        settings.set("Video", "Width",  str(gameResolution["width"]))
        settings.set("Video", "Height", str(gameResolution["height"]))

        if not settings.has_section("Config"):
            settings.add_section("Config")
        settings.set("Config", "GameWidth",  str(gameResolution["width"]))
        settings.set("Config", "GameHeight", str(gameResolution["height"]))
        settings.set("Config", "Language", "en")

        # Save config
        if not os.path.exists(os.path.dirname(settings_path)):
            os.makedirs(os.path.dirname(settings_path))

        with open(settings_path, 'w') as configfile:
            settings.write(configfile)

        commandArray = ["batocera-wine", "mugen", "play", rom]
        return Command.Command(array=commandArray, env={ "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers) })
