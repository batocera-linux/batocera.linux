#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
from utils.logger import get_logger
import controllersConfig
import os

eslog = get_logger(__name__)
PICO8_BIN_PATH="/userdata/bios/pico-8/pico8"
PICO8_ROOT_PATH="/userdata/roms/pico8/"
PICO8_CONTROLLERS="/userdata/system/.lexaloffle/pico-8/sdl_controllers.txt"
VOX_BIN_PATH="/userdata/bios/voxatron/vox"
VOX_ROOT_PATH="/userdata/roms/voxatron/"
VOX_CONTROLLERS="/userdata/system/.lexaloffle/Voxatron/sdl_controllers.txt"


# Generator for the official pico8 binary from Lexaloffle
class LexaloffleGenerator(Generator):
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        if (system.name == "pico8"):
            BIN_PATH=PICO8_BIN_PATH
            CONTROLLERS=PICO8_CONTROLLERS
            ROOT_PATH=PICO8_ROOT_PATH
        elif (system.name == "voxatron"):
            BIN_PATH=VOX_BIN_PATH
            CONTROLLERS=VOX_CONTROLLERS
            ROOT_PATH=VOX_ROOT_PATH
        else:
            eslog.error(f"The Lexaloffle generator has been called for an unknwon system: {system.name}.")
            return -1
        if not os.path.exists(BIN_PATH):
            eslog.error(f"Lexaloffle official binary not found at {BIN_PATH}")
            return -1
        if not os.access(BIN_PATH, os.X_OK):
            eslog.error(f"File {BIN_PATH} is not set as executable")
            return -1

        # the command to run
        commandArray = [BIN_PATH]
        commandArray.extend(["-desktop", "/userdata/screenshots"])  # screenshots
        commandArray.extend(["-windowed", "0"])                     # full screen
        # Display FPS
        if system.config['showFPS'] == 'true':
                commandArray.extend(["-show_fps", "1"])
        else:
                commandArray.extend(["-show_fps", "0"])

        basename = os.path.basename(rom)
        rombase, romext = os.path.splitext(basename)

        # .m3u support for multi-cart pico-8
        if (romext.lower() == ".m3u"):
            with open(rom, "r") as fpin:
                lines = fpin.readlines()
            fullpath = os.path.dirname(os.path.abspath(rom)) + '/' + lines[0].strip()
            localpath, localrom = os.path.split(fullpath)
            commandArray.extend(["-root_path", localpath])
            rom = fullpath
        else:
            commandArray.extend(["-root_path", ROOT_PATH]) # store carts from splore

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

    def getInGameRatio(self, config, gameResolution, rom):
        return 4/3
