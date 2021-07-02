#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
from utils.logger import eslog
import controllersConfig
import os

BIN_PATH="/userdata/bios/pico-8/pico8"

# Generator for the official pico8 binary from Lexaloffle
class LexaloffleGenerator(Generator):
    def generate(self, system, rom, playersControllers, gameResolution):
        if not os.path.exists(BIN_PATH):
            eslog.log("Lexaloffle official pico-8 binary not found at {}".format(BIN_PATH))
            return -1
        if not os.access(BIN_PATH, os.X_OK):
            eslog.log("File {} is not set as executable".format(BIN_PATH))
            return -1
        commandArray = [BIN_PATH]
        commandArray.extend(["-desktop", "/userdata/screenshots"])
        rombase=os.path.basename(rom) 
        idx=rombase.index('.')
        rombase=rombase[:idx]
        if (rombase.lower() == "splore" or rombase.lower() == "console"):
            commandArray.extend(["-splore"])
        else:
            commandArray.extend(["-run", rom])
        env = {}
        env["SDL_GAMECONTROLLERCONFIG"] = controllersConfig.generateSdlGameControllerConfig(playersControllers)

        return Command.Command(array=commandArray, env=env)
