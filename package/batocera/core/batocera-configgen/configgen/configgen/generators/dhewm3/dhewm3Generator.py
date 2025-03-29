from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import CONFIGS, ROMS, SAVES, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from pathlib import Path

    from ...types import HotkeysContext

_logger = logging.getLogger(__name__)

_DHEWM3_CONFIG: Final = CONFIGS / "dhewm3"

class Dhewm3Generator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "dhewm3",
            "keys": {
                "exit": ["KEY_LEFTALT", "KEY_F4"],
                "save_state": "KEY_F5",
                "restore_state": "KEY_F9"
            }
        }

    def generate(self, system, rom, playersControllers, metadata, esmetadata, guns, wheels, gameResolution):

        # Set the paths using Path objects
        romDir = ROMS / "doom3"
        # Read the path within the .d3 rom file
        with rom.open() as file:
            directory = file.readline().strip().split("/")[0]
            _logger.debug("Using directory: %s", directory)

        _DHEWM3_CONFIG_BASE_DIR = _DHEWM3_CONFIG / "base"
        _DHEWM3_CONFIG_DIR = _DHEWM3_CONFIG / directory
        _DHEWM3_CONFIG_BASE_FILE = _DHEWM3_CONFIG_BASE_DIR / "dhewm.cfg"
        _DHEWM3_CONFIG_FILE = _DHEWM3_CONFIG_DIR / "dhewm.cfg"

        mkdir_if_not_exists(_DHEWM3_CONFIG_BASE_DIR)
        mkdir_if_not_exists(_DHEWM3_CONFIG_DIR)

        options_to_set = {
            "seta r_mode": "-1",
            "seta r_fullscreen": "1",
            "seta r_customHeight": f'{gameResolution["height"]}',
            "seta r_customWidth": f'{gameResolution["width"]}',
            'bind "JOY_BTN_SOUTH"': "_moveUp",
            'bind "JOY_BTN_EAST"': "_moveDown",
            'bind "JOY_BTN_WEST"': "_impulse19",
            'bind "JOY_BTN_NORTH"': "_impulse13",
            'bind "JOY_BTN_LSTICK"': "_strafe",
            'bind "JOY_BTN_RSTICK"': "_speed",
            'bind "JOY_BTN_LSHOULDER"': "_impulse15",
            'bind "JOY_BTN_RSHOULDER"': "_impulse14",
            'bind "JOY_STICK1_UP"': "_forward",
            'bind "JOY_STICK1_DOWN"': "_back",
            'bind "JOY_STICK1_LEFT"': "_moveLeft",
            'bind "JOY_STICK1_RIGHT"': "_moveRight",
            'bind "JOY_STICK2_UP"': "_lookUp",
            'bind "JOY_STICK2_DOWN"': "_lookDown",
            'bind "JOY_STICK2_LEFT"': "_left",
            'bind "JOY_STICK2_RIGHT"': "_right",
            'bind "JOY_TRIGGER2"': "_attack"
        }

        ## ES options
        # Set brightness
        options_to_set["seta r_brightness"] = system.config.get("dhewm3_brightness", "1")
        # Game language
        options_to_set["seta sys_lang"] = system.config.get("dhewm3_language", "english")

        def update_config_file(file_path: Path):
            if file_path.is_file():
                with file_path.open('r') as config_file:
                    lines = config_file.readlines()

                # Loop through the options and update the lines
                for key, value in options_to_set.items():
                    option_exists = any(key in line for line in lines)
                    if not option_exists:
                        lines.append(f"{key} \"{value}\"\n")
                    else:
                        for i, line in enumerate(lines):
                            if key in line:
                                lines[i] = f"{key} \"{value}\"\n"

                # Write the modified content back to the file
                with file_path.open('w') as config_file:
                    config_file.writelines(lines)
            else:
                # File doesn't exist, create it and add the options
                with file_path.open('w') as config_file:
                    for key, value in options_to_set.items():
                        config_file.write(f"{key} \"{value}\"\n")

        # Update both config files
        update_config_file(_DHEWM3_CONFIG_BASE_FILE)
        update_config_file(_DHEWM3_CONFIG_FILE)

        # Run command
        commandArray: list[str | Path] = [
            "/usr/bin/dhewm3", "+set", "fs_basepath", romDir
        ]

        if directory == "perfected_roe" or directory == "sikkmodd3xp":
            commandArray.extend(
                ["+set", "fs_game_base", "d3xp"]
            )

        if directory == "d3le":
            commandArray.extend(
                ["+set", "fs_game_base", "d3xp", "+seta", "com_allowconsole", "1"]
            )

        if directory != "base":
            commandArray.extend(
                ["+set", "fs_game", str(directory)]
            )

        return Command.Command(
            array=commandArray,
            env={
                "XDG_CONFIG_HOME": CONFIGS,
                "XDG_DATA_HOME": SAVES,
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9
