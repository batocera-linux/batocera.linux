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

from typing import TYPE_CHECKING, Final

import shutil
import os
from ... import Command
from ...batoceraPaths import CONFIGS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...config import SystemConfig
    from ...types import HotkeysContext, Resolution

_OPENJKDF2_CONFIG: Final = CONFIGS / "openjkdf2"


class OpenJKDF2Generator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "openjkdf2",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        mkdir_if_not_exists(_OPENJKDF2_CONFIG)

        # TODO - config & copy to each user

        # TODO - controller

        romdir = rom.parent
        binary_src = "/usr/bin/openjkdf2"
        binary_dest = romdir / "openjkdf2"

        # Check if the binary exists in the destination and if it is outdated
        if not binary_dest.exists() or os.path.getmtime(binary_src) > os.path.getmtime(binary_dest):
            shutil.copy2(binary_src, binary_dest)
        
        os.chdir(romdir)
        
        commandArray = [str(binary_dest)]

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
        return 16/9
