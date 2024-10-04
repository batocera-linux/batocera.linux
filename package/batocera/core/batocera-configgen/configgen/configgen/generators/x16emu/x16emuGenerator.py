import configparser
import os

from ...batoceraPaths import CONFIGS
from ... import Command
from ... import controllersConfig
from ..Generator import Generator

class X16emuGenerator(Generator):

    def getHotkeysContext(self):
        return {
            "name": "x16emu",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # set the file system path
        romdir = os.path.dirname(rom)
        # default options
        commandArray = [
            "x16emu",
            "-rom", "/userdata/bios/commanderx16/rom.bin", # bios
            "-fsroot", romdir, # file system
            "-ram", "2048", # specify 2MB of RAM by default
            "-rtc", # realtime clock
            "-fullscreen", # run fullscreen
            "-prg", rom, # program to run
            "-run" # run the program
        ]

        if system.isOptSet("x16emu_scale"):
            commandArray.extend(["-scale", system.config["x16emu_scale"]])
        else:
            commandArray.extend(["-scale", "2"]) # 1280 x 960
        
        if system.isOptSet("x16emu_quality"):
            commandArray.extend(["-quality", system.config["x16emu_quality"]])
        
        if system.isOptSet("x16emu_ratio") and system.config["x16emu_ratio"] == "16:9":
            commandArray.extend(["-widescreen"])
        
        # Now add Controllers
        nplayer = 1
        for controller, pad in sorted(playersControllers.items()):
            if nplayer <= 4:
                commandArray.extend([f"-joy{nplayer}"])
            nplayer += 1

        return Command.Command(
            array=commandArray,
            env={
                "XDG_DATA_HOME": CONFIGS,
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if ("x16emu_ratio" in config and config["x16emu_ratio"] == "16:9"):
            return 16/9
        return 4/3
