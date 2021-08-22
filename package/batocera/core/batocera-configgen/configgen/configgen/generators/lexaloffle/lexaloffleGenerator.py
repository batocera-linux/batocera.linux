#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
from utils.logger import get_logger
import controllersConfig
import os

eslog = get_logger(__name__)
BIN_PATH="/userdata/bios/pico-8/pico8"
CONTROLLERS="/userdata/system/.lexaloffle/pico-8/sdl_controllers.txt"

# Generator for the official pico8 binary from Lexaloffle
class LexaloffleGenerator(Generator):
    def generate(self, system, rom, playersControllers, gameResolution):
        if not os.path.exists(BIN_PATH):
            eslog.error("Lexaloffle official pico-8 binary not found at {}".format(BIN_PATH))
            return -1
        if not os.access(BIN_PATH, os.X_OK):
            eslog.error("File {} is not set as executable".format(BIN_PATH))
            return -1

        # the command to run
        commandArray = [BIN_PATH]
        commandArray.extend(["-desktop", "/userdata/screenshots"])  # screenshots
        commandArray.extend(["-root_path", "/userdata/roms/pico8"]) # store carts from splore
        commandArray.extend(["-windowed", "0"])                     # full screen
        # Display FPS
        if system.config['showFPS'] == 'true':
                commandArray.extend(["-show_fps", "1"])
        else:
                commandArray.extend(["-show_fps", "0"])

        rombase=os.path.basename(rom) 
        idx=rombase.index('.')
        rombase=rombase[:idx]
        if (rombase.lower() == "splore" or rombase.lower() == "console"):
            commandArray.extend(["-splore"])
        else:
            commandArray.extend(["-run", rom])

        controllersdir = os.path.dirname(CONTROLLERS)
        if not os.path.exists(controllersdir):
                os.makedirs(controllersdir)
        controllersconfig = controllersConfig.generateSdlGameControllerConfig(playersControllers)
        with open(CONTROLLERS, "w") as file:
               file.write(controllersconfig)

        return Command.Command(array=commandArray, env={})
