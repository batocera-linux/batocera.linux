#!/usr/bin/env python

import os
from configobj import ConfigObj
import batoceraFiles
from generators.Generator import Generator
import controllersConfig
import Command
import shutil

class CGeniusGenerator(Generator):
    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):

        cgeniusCtrl = {
            "a":              "Fire",
            "b":              "Jump",
            "pageup":         "Camlead",
            "x":              "Status",
            "y":              "Pogo",
            "pagedown":       "Run",
            "up":             "Up",
            "down":           "Down",
            "left":           "Left",
            "right":          "Right"
        }

        # Define the directory and file name for the config file
        config_dir = batoceraFiles.CONF + "/cgenius"
        alt_config_dir = "/userdata/roms/cgenius"
        config_file = "cgenius.cfg"
        config_path = os.path.join(config_dir, config_file)

        # Create the config directory if it doesn't exist
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
       
        if not os.path.exists(config_path):
            config = ConfigObj()
            config.filename = config_path
        else:
            config = ConfigObj(infile=config_path)

        # Now setup the options we want...
        if "FileHandling" not in config:
            config["FileHandling"] = {}
        config["FileHandling"]["EnableLogfile"] = "false"
        config["FileHandling"]["SearchPath1"] = "/userdata/roms/cgenius"
        config["FileHandling"]["SearchPath2"] = "/userdata/roms/cgenius/games"

        if "Video" not in config:
            config["Video"] = {}
        # aspect
        if system.isOptSet("cgenius_aspect"):
            config["Video"]["aspect"] = system.config["cgenius_aspect"]
        else:
            config["Video"]["aspect"] = "4:3"
        # we always want fullscreen
        config["Video"]["fullscreen"] = "true"
        # filter
        if system.isOptSet("cgenius_filter"):
            config["Video"]["filter"] = system.config["cgenius_filter"]
        else:
            config["Video"]["filter"] = "none"
        # quality
        if system.isOptSet("cgenius_quality"):
            config["Video"]["OGLfilter"] = system.config["cgenius_quality"]
        else:
            config["Video"]["OGLfilter"] = "nearest"
        # render resolution
        if system.isOptSet("cgenius_render"):
            if system.config["cgenius_render"] == "200":
                config["Video"]["gameHeight"] = "200"
                config["Video"]["gameWidth"] = "320"
            if system.config["cgenius_render"] == "240":
                config["Video"]["gameHeight"] = "240"
                config["Video"]["gameWidth"] = "320"
            if system.config["cgenius_render"] == "360":
                config["Video"]["gameHeight"] = "360"
                config["Video"]["gameWidth"] = "640"
            if system.config["cgenius_render"] == "480":
                config["Video"]["gameHeight"] = "480"
                config["Video"]["gameWidth"] = "640"
        else:
            config["Video"]["gameHeight"] = "200"
            config["Video"]["gameWidth"] = "320"
        # mouse
        if system.isOptSet("cgenius_cursor"):
            config["Video"]["ShowCursor"] = system.config["cgenius_cursor"]
        else:
            config["Video"]["ShowCursor"] = "false"

        # -= Controllers =-
        # Configure the first four controllers
        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            if nplayer <= 4:
                input_num = "input" + str(pad.index)
                if input_num not in config:
                    config[input_num] = {}
                for x in pad.inputs:
                    input = pad.inputs[x]
                    if input.name in cgeniusCtrl:
                        if input.type == "hat":
                            config[input_num][cgeniusCtrl[input.name]] = "Joy" + str(pad.index) + "-" + input.type[0].upper() + str(input.value)
                        else:
                            config[input_num][cgeniusCtrl[input.name]] = "Joy" + str(pad.index) + "-" + input.type[0].upper() + str(input.id)
                nplayer += 1
        
        # Write the config file
        config.write()
        # need to copy to roms folder too
        shutil.copy(config_path, alt_config_dir)

        # now setup to run the rom
        commandArray = ["CGeniusExe"]
        # get rom path
        rom_path = os.path.dirname(rom)
        rom_path = rom_path.replace("/userdata/roms/cgenius/", "")
        dir_string = "dir=\"" + rom_path + "\""
        commandArray.append(dir_string)

        return Command.Command(
            array=commandArray,
            env={"SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)}
        )

    # Show mouse on screen for the Config Screen
    def getMouseMode(self, config):
        return True
