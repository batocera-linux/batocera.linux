from __future__ import annotations
import os
from typing import TYPE_CHECKING, Final
from ... import Command
from ...batoceraPaths import BIOS, HOME, ROMS, SCREENSHOTS, ensure_parents_and_open
from ...controller import generate_sdl_game_controller_config
from ...exceptions import BatoceraException
from ..Generator import Generator

if TYPE_CHECKING:
    from pathlib import Path
    from ...types import HotkeysContext

class NesboxGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "nesbox",
            "keys": { "exit": ["KEY_LEFTCTRL", "KEY_Q"], "menu": "KEY_ENTER", "reset": [ "KEY_LEFTCTRL", "KEY_R" ] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray: list[str | Path] = ["tic80"]
        rombase = rom.stem

        if (rombase.lower() == "surf" or rombase.lower() == "console"):
            commandArray.extend(["--cmd=surf"])
        else:
            commandArray.extend([rom])

        controllersconfig = generate_sdl_game_controller_config(playersControllers)
        with ensure_parents_and_open(CONTROLLERS, "w") as file:
               file.write(controllersconfig)

        existing_library_path = os.environ.get("LD_LIBRARY_PATH")

        return Command.Command(array=commandArray, env={
            "LD_LIBRARY_PATH": f"{LD_LIB}:{existing_library_path}" if existing_library_path else LD_LIB
        })

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
