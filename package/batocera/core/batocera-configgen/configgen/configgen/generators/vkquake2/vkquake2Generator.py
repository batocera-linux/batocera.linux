from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import ROMS
from ...controller import generate_sdl_game_controller_config
from ...exceptions import BatoceraException
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

vkquake2RomPath = ROMS / "quake2"
vkquake2Binary = vkquake2RomPath / "quake2"
vkquake2SourcePath = Path("/usr/bin/vkquake2")

class VKQuake2Generator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "vkquake2",
            "keys": { "exit": "KEY_F10", "save_state": "KEY_F6", "restore_state": "KEY_F7" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        romName = Path(rom).name

        # Copy updated binary files if they don't exist or if the source is newer
        if vkquake2SourcePath.exists():
            shutil.copytree(vkquake2SourcePath, vkquake2RomPath, dirs_exist_ok=True, copy_function=shutil.copy2)
        else:
            raise BatoceraException(f"Source directory {vkquake2SourcePath} does not exist.")

        # Change to the rom directory before running
        os.chdir(vkquake2RomPath)

        commandArray = [ vkquake2Binary ]

        # Mission Packs
        if "zero" in romName.lower():
            commandArray.extend(["+set", "game", "rogue"])
        if "reckoning" in romName.lower():
            commandArray.extend(["+set", "game", "xatrix"])
        if "zaero" in romName.lower():
            commandArray.extend(["+set", "game", "zaero"])
        if "destruction" in romName.lower():
            commandArray.extend(["+set", "game", "smd"])

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers),
                'SDL_JOYSTICK_HIDAPI': '0'
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if gameResolution["width"] / float(gameResolution["height"]) > ((16.0 / 9.0) - 0.1):
            return 16/9
        return 4/3
