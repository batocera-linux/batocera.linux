#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
from os import path
import controllersConfig


class WineGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        if system.name == "windows_installers":
            commandArray = ["batocera-wine", "windows", "install", rom]
            return Command.Command(array=commandArray)
        elif system.name == "windows":
            if os.path.exists(rom + "/autorun.cmd"):
                with open(rom + "/autorun.cmd") as fp:
                    for line in fp:
                        if line.startswith("LANG="):
                            newLang = (line.rstrip()).split("=")
                            os.environ["LANG"] = newLang[1]
                            os.environ["LANGUAGE"] = newLang[1]
                            os.environ["LC_ALL"] = newLang[1]
            commandArray = ["batocera-wine", "windows", "play", rom]
            return Command.Command(array=commandArray,env={
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers),
            })

        raise Exception("invalid system " + system.name)

    def getMouseMode(self, config):
        if "force_mouse" in config and config["force_mouse"] == "0":
            return False
        else:
            return True
