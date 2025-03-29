from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final
from pathlib import Path

from ... import Command
from ...batoceraPaths import CONFIGS, ROMS, SAVES, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

_logger = logging.getLogger(__name__)

_BSTONE_CONFIG: Final = CONFIGS / "bstone"
_BSTONE_CONFIG_FILE = _BSTONE_CONFIG / "bstone_config.txt"

def update_or_create_config(gameResolution):
    default_config = f"""// BStone configuration file
// WARNING! This is auto-generated file.

vid_width "{str(gameResolution['width'])}"
vid_height "{str(gameResolution['height'])}"
"""
    
    if _BSTONE_CONFIG_FILE.exists():
        with _BSTONE_CONFIG_FILE.open("r") as f:
            lines = f.readlines()
        
        updated_lines = []
        for line in lines:
            if line.startswith("vid_width"):
                updated_lines.append(f'vid_width "{str(gameResolution["width"])}"\n')
            elif line.startswith("vid_height"):
                updated_lines.append(f'vid_height "{str(gameResolution["height"])}"\n')
            else:
                updated_lines.append(line)
        
        with _BSTONE_CONFIG_FILE.open("w") as f:
            f.writelines(updated_lines)
    else:
        with _BSTONE_CONFIG_FILE.open("w") as f:
            f.write(default_config)

class BstoneGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "bstone",
            "keys": {
                "exit": "KEY_F10",
                "save_state": "KEY_F2",
                "restore_state": "KEY_F3",
                "menu": "KEY_ESC",
                "screenshot": "KEY_F5"
            },
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        mkdir_if_not_exists(_BSTONE_CONFIG)
        update_or_create_config(gameResolution)

        romdir = rom.parent

        filename_to_flag = {
            "audiohed.bs1": "--aog_sw",
            "audiohed.bs6": "--aog",
            "audiohed.vsi": "--ps"
        }

        version_flags = set()
        for file in romdir.iterdir():
            if file.is_file() and file.name.lower() in filename_to_flag:
                version_flags.add(filename_to_flag[file.name.lower()])

        commandArray = ["/usr/bin/bstone", "--profile_dir", _BSTONE_CONFIG, "--data_dir", romdir]
        commandArray.extend(version_flags)

        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9
