from __future__ import annotations

import codecs
import os
from shlex import split
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

    def generate(self, system, rom, playersControllers, metadata, esmetadata, guns, wheels, gameResolution):
        ecwolfConfigDir = CONFIGS / "ecwolf"
        ecwolfConfigFile = ecwolfConfigDir / "ecwolf.cfg"
        ecwolfSaves = SAVES / "ecwolf" / rom.name
        ecwolfArray = ["ecwolf"] # Binary for command array

        # Create config folders
        mkdir_if_not_exists(ecwolfConfigDir)

        # Create config file if not there
        if not ecwolfConfigFile.is_file():
            with codecs.open(str(ecwolfConfigFile), "x") as f:
                f.write('Vid_FullScreen = 1;\n')
                f.write('Vid_Aspect = 0;\n')
                f.write('Vid_Vsync = 1;\n')
                f.write('QuitOnEscape = 1;\n')

        # Set the resolution and some other defaults
        if ecwolfConfigFile.is_file():
            #We ignore some options in default config with py-dictonary...
            IgnoreConfigKeys = {"FullScreenWidth", "FullScreenHeight", "JoystickEnabled"}
            with codecs.open(str(ecwolfConfigFile), "r") as f:
                lines = list(f)

            # ... write all the non ignored keys back to config file ...
            with codecs.open(str(ecwolfConfigFile), "w") as f:
                for line in lines:
                    if not IgnoreConfigKeys.intersection(line.split()):
                        f.write(line)

            # ... and append the ignored keys with default values now ;)
            with codecs.open(str(ecwolfConfigFile), "a") as f:
                f.write('JoystickEnabled = 1;\n')
                f.write(f'FullScreenWidth = {gameResolution["width"]};\n')
                f.write(f'FullScreenHeight = {gameResolution["height"]};\n')

        # Create save folder, according rom name with extension
        mkdir_if_not_exists(ecwolfSaves)

        # Use the directory method with ecwolf extension and datafiles (wl6 or sod or nh3) inside
        if rom.is_dir():
            try:
                os.chdir(rom)
            # Only game directories, not .ecwolf or .pk3 files
            except Exception as e:
                print(f"Error: couldn't go into directory {rom} ({e})")

        # File method .ecwolf (recommended) for command parameters, first argument is path to dataset,
        # next parameters according ecwolf --help, use doublequotes if path or filenames contains spaces
        # File method .pk3, put pk3 files next to wl6 dataset and start the mod in ES
        if rom.is_file():
            os.chdir(rom.parent)
            fextension = rom.suffix.lower()

            if fextension == ".ecwolf":
                with codecs.open(str(rom),"r") as f:
                    ecwolfArray += split(f)

                # If 1. parameter isn't an argument then assume it's a path
                if "--" not in ecwolfArray[1]:
                    try:
                        os.chdir(ecwolfArray[1])
                    except Exception as e:
                        print(f"Error: couldn't go into directory {ecwolfArray[1]} ({e})")
                    ecwolfArray.pop(1)

            if fextension == ".pk3":
                ecwolfArray += ["--file", rom.name]

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
