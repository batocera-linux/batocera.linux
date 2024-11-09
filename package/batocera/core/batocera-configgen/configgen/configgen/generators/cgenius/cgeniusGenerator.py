from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from configobj import ConfigObj

from ... import Command
from ...batoceraPaths import CONFIGS, ROMS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


class CGeniusGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "cgenius",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_ESC", "pause": "KEY_ESC", "save_state": "KEY_F6" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

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
        config_dir = CONFIGS / "cgenius"
        alt_config_dir = ROMS / "cgenius"
        config_path = config_dir / "cgenius.cfg"

        # Create the config directory if it doesn't exist
        mkdir_if_not_exists(config_dir)

        if not config_path.exists():
            config = ConfigObj()
            config.filename = str(config_path)
        else:
            config = ConfigObj(infile=str(config_path))

        # Now setup the options we want...
        if "FileHandling" not in config:
            config["FileHandling"] = {}
        config["FileHandling"]["EnableLogfile"] = "false"
        config["FileHandling"]["SearchPath1"] = str(alt_config_dir)
        config["FileHandling"]["SearchPath2"] = str(alt_config_dir / "games")

        if "Video" not in config:
            config["Video"] = {}
        # aspect
        if system.isOptSet("cgenius_aspect"):
            config["Video"]["aspect"] = system.config["cgenius_aspect"]
        else:
            config["Video"]["aspect"] = "4:3"
        # set false as we want the correct ratio
        config["Video"]["fullscreen"] = "false"
        config["Video"]["integerScaling"] = "false"
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
        rom_path = Path(rom).parent
        rom_path = rom_path.relative_to(alt_config_dir) if rom_path.is_relative_to(alt_config_dir) else rom_path
        commandArray.append(f'dir="{rom_path}"')

        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    # Show mouse on screen for the Config Screen
    def getMouseMode(self, config, rom):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        if 'cgenius_aspect' in config:
            if config['cgenius_aspect'] == "16:9" or config['cgenius_aspect'] == "16:10":
                return 16/9
            else:
                return 4/3
        else:
            return 4/3
