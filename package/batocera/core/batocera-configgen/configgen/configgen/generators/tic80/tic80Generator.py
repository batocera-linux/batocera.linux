from __future__ import annotations
import os
from typing import TYPE_CHECKING, Final
from ... import Command
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from pathlib import Path
    from ...types import HotkeysContext

class tic80Generator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "tic80",
            "keys": { "exit": ["KEY_LEFTCTRL", "KEY_Q"], "menu": "KEY_ENTER", "reset": [ "KEY_LEFTCTRL", "KEY_R" ] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray: list[str | Path] = ["tic80", "--fullscreen", "--skip"]
        rombase = rom.stem

        if (rombase.lower() == "surf" or rombase.lower() == "console"):
            commandArray.extend(["--cmd=surf"])
        else:
            commandArray.extend([rom])

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers)
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
