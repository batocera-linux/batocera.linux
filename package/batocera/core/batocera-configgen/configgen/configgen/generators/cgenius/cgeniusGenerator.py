from __future__ import annotations

import shutil
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
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_ESC", "pause": "KEY_ESC", "save_state": "KEY_F6", "restore_state": "KEY_F9" }
        }

    def generate(self, system, rom, playersControllers, metadata, esmetadata, guns, wheels, gameResolution):

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
        config["Video"]["aspect"] = system.config.get("cgenius_aspect", "4:3")
        # set false as we want the correct ratio
        config["Video"]["fullscreen"] = "false"
        config["Video"]["integerScaling"] = "false"
        # filter
        config["Video"]["filter"] = system.config.get("cgenius_filter", "none")
        # quality
        config["Video"]["OGLfilter"] = system.config.get("cgenius_quality", "nearest")
        # render resolution
        match system.config.get("cgenius_render"):
            case "240":
                config["Video"]["gameHeight"] = "240"
                config["Video"]["gameWidth"] = "320"
            case "360":
                config["Video"]["gameHeight"] = "360"
                config["Video"]["gameWidth"] = "640"
            case "480":
                config["Video"]["gameHeight"] = "480"
                config["Video"]["gameWidth"] = "640"
            case _:
                config["Video"]["gameHeight"] = "200"
                config["Video"]["gameWidth"] = "320"
        # mouse
        config["Video"]["ShowCursor"] = system.config.get("cgenius_cursor", "false")

        # -= Controllers =-
        # Configure the first four controllers
        for pad in playersControllers[:4]:
            input_num = f"input{pad.index}"
            if input_num not in config:
                config[input_num] = {}
            for x in pad.inputs:
                input = pad.inputs[x]
                if input.name in cgeniusCtrl:
                    if input.type == "hat":
                        config[input_num][cgeniusCtrl[input.name]] = f"Joy{pad.index}-{input.type[0].upper()}{input.value}"
                    else:
                        config[input_num][cgeniusCtrl[input.name]] = f"Joy{pad.index}-{input.type[0].upper()}{input.id}"

        # Write the config file
        config.write()
        # need to copy to roms folder too
        shutil.copy(config_path, alt_config_dir)

        # now setup to run the rom
        commandArray = ["CGeniusExe"]
        # get rom path
        rom_path = rom.parent
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
        aspect = config.get('cgenius_aspect')
        if aspect == "16:9" or aspect == "16:10":
            return 16/9
        return 4/3
