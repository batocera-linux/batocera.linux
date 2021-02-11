#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
import controllersConfig
import ConfigParser

class MugenGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        settings = ConfigParser.ConfigParser()
        # To prevent ConfigParser from converting to lower case
        settings.optionxform = str
        settings_path = rom + "/mugen/mugen.cfg"
        if os.path.exists(settings_path):
            settings.read(settings_path)

        if not settings.has_section("Video"):
            settings.add_section("Video")
        settings.set("Video", "FullScreen", "1")
        #settings.set("Video", "Width",  gameResolution["width"])
        #settings.set("Video", "Height", gameResolution["height"])

        if not settings.has_section("Config"):
            settings.add_section("Config")
        #settings.set("Config", "GameWidth",  gameResolution["width"])
        #settings.set("Config", "GameHeight", gameResolution["height"])
        settings.set("Config", "Language", "en")

        # Save config
        if not os.path.exists(os.path.dirname(settings_path)):
            os.makedirs(os.path.dirname(settings_path))

        with open(settings_path, 'w') as configfile:
            settings.write(configfile)

        commandArray = ["batocera-wine", "mugen", "play", rom]
        return Command.Command(array=commandArray, env={ "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers) })
