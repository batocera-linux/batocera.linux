from __future__ import annotations

import codecs
import os
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, SAVES, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


class ECWolfGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "ecwolf",
            "keys": { 
                "exit": ["KEY_LEFTALT", "KEY_F4"],
                "menu": "KEY_ESC",
                "pause": "KEY_ESC",
                "save_state": "KEY_F8",
                "restore_state": "KEY_F9"
            }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        rom_path = Path(rom)

        ecwolfConfigDir = CONFIGS / "ecwolf"
        ecwolfConfigFile = ecwolfConfigDir / "ecwolf.cfg"
        ecwolfSaves = SAVES / "ecwolf" / rom_path.name
        ecwolfArray = ["ecwolf"] # Binary for command array

        # Create config folders
        mkdir_if_not_exists(ecwolfConfigDir)

        # Create config file if not there
        if not ecwolfConfigFile.is_file():
            f = codecs.open(str(ecwolfConfigFile), "x")
            f.write('Vid_FullScreen = 1;\n')
            f.write('Vid_Aspect = 0;\n')
            f.write('Vid_Vsync = 1;\n')
            f.write('QuitOnEscape = 1;\n')
            f.write('FullScreenWidth = {};\n'.format(gameResolution["width"]))
            f.write('FullScreenHeight = {};\n'.format(gameResolution["height"]))
            f.close()

        # Set the resolution and some other defaults
        if ecwolfConfigFile.is_file():
            #We ignore some options in default config with py-dictonary...
            IgnoreConfigKeys = {"FullScreenWidth", "FullScreenHeight", "JoystickEnabled"}
            with codecs.open(str(ecwolfConfigFile), "r") as f:
                lines = {line for line in f}

            # ... write all the non ignored keys back to config file ...
            with codecs.open(str(ecwolfConfigFile), "w") as f:
                for line in lines:
                    if not IgnoreConfigKeys.intersection(line.split()):
                        f.write(line)

            # ... and append the ignored keys with default values now ;)
            f = codecs.open(str(ecwolfConfigFile), "a")
            f.write('JoystickEnabled = 1;\n')
            f.write('FullScreenWidth = {};\n'.format(gameResolution["width"]))
            f.write('FullScreenHeight = {};\n'.format(gameResolution["height"]))
            f.close()

        # Create save folder, according rom name with extension
        mkdir_if_not_exists(ecwolfSaves)

        # Use the directory method with ecwolf extension and datafiles (wl6 or sod or nh3) inside
        if rom_path.is_dir():
            try:
                os.chdir(rom_path)
            # Only game directories, not .ecwolf or .pk3 files
            except Exception as e:
                print(f"Error: couldn't go into directory {rom_path} ({e})")

        # File method .ecwolf (recommended) for command parameters, first argument is path to dataset,
        # next parameters according ecwolf --help
        # File method .pk3, put pk3 files next to wl6 dataset and start the mod in ES
        if rom_path.is_file():
            os.chdir(rom_path.parent)
            fextension = rom_path.suffix.lower()

            if fextension == ".ecwolf":
                with codecs.open(str(rom_path),"r") as f:
                    ecwolfArray += (f.readline().split())

                # If 1. parameter isn't an argument then assume it's a path
                if not "--" in ecwolfArray[1]:
                    try:
                        os.chdir(ecwolfArray[1])
                    except Exception as e:
                        print(f"Error: couldn't go into directory {ecwolfArray[1]} ({e})")
                    ecwolfArray.pop(1)

            if fextension == ".pk3":
                ecwolfArray += ["--file", rom_path.name]

        ecwolfArray += [
                 #Use values according ecwolf --help, do not miss any parameter
                 "--savedir", ecwolfSaves
        ]

        return Command.Command(
             ecwolfArray,
             env={
                'XDG_CONFIG_HOME': CONFIGS,
                'XDG_DATA_HOME': SAVES,
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers)
            }
        )
