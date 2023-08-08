#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
from os import path
import controllersConfig
import subprocess

class WineGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        if system.name == "windows_installers":
            commandArray = ["batocera-wine", "windows", "install", rom]
            return Command.Command(array=commandArray)
        elif system.name == "windows":
            commandArray = ["batocera-wine", "windows", "play", rom]
            
            environment = {}
            #system.language
            language = subprocess.check_output("batocera-settings-get system.language", shell=True, text=True).strip()
            if language:
                environment.update({
                    "LANG": language + ".UTF-8",
                    "LC_ALL": language + ".UTF-8"
                    }
                )
            # sdl controller option
            if system.isOptSet("sdl_config") and system.getOptBoolean("sdl_config"):
                environment.update({
                    "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers),
                    "SDL_JOYSTICK_HIDAPI": "0"
                    }
                )
            return Command.Command(array=commandArray, env=environment)
        
        raise Exception("invalid system " + system.name)

    def getMouseMode(self, config):
        if "force_mouse" in config and config["force_mouse"] == "0":
            return False
        else:
            return True
