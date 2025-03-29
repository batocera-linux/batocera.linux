#
# This file is part of the batocera distribution (https://batocera.org).
# Copyright (c) 2025+.
#
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# YOU MUST KEEP THIS HEADER AS IT IS
#
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
    from ... import SystemConfig

_logger = logging.getLogger(__name__)

_BSTONE_CONFIG: Final = CONFIGS / "bstone"
_BSTONE_CONFIG_FILE = _BSTONE_CONFIG / "bstone_config.txt"


def update_or_create_config(gameResolution: dict[str, int], system: SystemConfig):
    config_lines: list[str] = []

    config_lines.append(f'vid_width "{gameResolution["width"]}"\n')
    config_lines.append(f'vid_height "{gameResolution["height"]}"\n')

    # Configuration options
    config_lines.append(f'vid_is_widescreen "{1 if system.config.get_bool("bstone_widescreen") else 0}"\n')
    config_lines.append(f'vid_is_vsync "{1 if system.config.get_bool("bstone_vsync") else 0}"\n')
    config_lines.append(f'vid_is_ui_stretched "{1 if system.config.get_bool("bstone_ui_stretched") else 0}"\n')

    # Handle existing file or create a new file
    if _BSTONE_CONFIG_FILE.exists():
        existing_lines = []
        with _BSTONE_CONFIG_FILE.open("r") as f:
            existing_lines = f.readlines()

        with _BSTONE_CONFIG_FILE.open("w") as f:
            for line in config_lines:
                # Check for a match in the existing lines
                match = False
                for i, existing_line in enumerate(existing_lines):
                    if line.split('"')[0] in existing_line:
                        existing_lines[i] = line
                        match = True
                        break

                # If there was no match, add to the config
                if not match:
                    existing_lines.append(line)

            f.writelines(existing_lines)

    else:
        # Create new file with all config lines
        with _BSTONE_CONFIG_FILE.open("w") as f:
            f.writelines(config_lines)


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
        update_or_create_config(gameResolution, system)

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
        if config.get_bool("bstone_widescreen") or config.get_bool("bstone_ui_stretched"):
            return 16/9
        return 4/3
