from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator
from . import ioquake3Config
from .ioquake3Paths import IOQUAKE3_ROMS

if TYPE_CHECKING:
    from ...types import HotkeysContext


class IOQuake3Generator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        rom_path = Path(rom)

        ioquake3Config.writeCfgFiles(system, rom_path, playersControllers, gameResolution)

        # ioquake3 looks for folder either in config or from where it's launched
        source_dir = Path("/usr/bin/ioquake3")
        destination_file = IOQUAKE3_ROMS / "ioquake3"
        source_file = source_dir / "ioquake3"
        # therefore copy latest ioquake3 file to rom directory
        if not destination_file.is_file() or source_file.stat().st_mtime > destination_file.stat().st_mtime:
            shutil.copytree(source_dir, IOQUAKE3_ROMS, dirs_exist_ok=True)

        commandArray = ["/userdata/roms/quake3/ioquake3"]

        # get the game / mod to launch
        with rom_path.open("r") as file:
            command_line = file.readline().strip()
            command_line_words = command_line.split()

        commandArray.extend(command_line_words)

        environment = {
            "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers)
        }

        return Command.Command(array=commandArray, env=environment)

    def getInGameRatio(self, config, gameResolution, rom):
        if gameResolution["width"] / float(gameResolution["height"]) > ((16.0 / 9.0) - 0.1):
            return 16/9
        return 4/3

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "ioquake3",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }
