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

PICO8_BIN_PATH: Final = BIOS / "pico-8" / "pico8"
PICO8_ROOT_PATH: Final = ROMS / "pico8"
PICO8_CONTROLLERS: Final = HOME / ".lexaloffle" / "pico-8" / "sdl_controllers.txt"
VOX_BIN_PATH: Final = BIOS / "voxatron" / "vox"
VOX_ROOT_PATH: Final = ROMS / "voxatron"
VOX_CONTROLLERS: Final = HOME / ".lexaloffle" / "Voxatron" / "sdl_controllers.txt"


# Generator for the official pico8 binary from Lexaloffle
class LexaloffleGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "lexaloffle",
            "keys": { "exit": ["KEY_LEFTCTRL", "KEY_Q"], "menu": "KEY_ENTER", "reset": [ "KEY_LEFTCTRL", "KEY_R" ] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        if (system.name == "pico8"):
            LD_LIB="LD_LIBRARY_PATH=$LD_LIBRARY_PATH:"+str(BIOS / "pico-8")
            BIN_PATH=PICO8_BIN_PATH
            CONTROLLERS=PICO8_CONTROLLERS
            ROOT_PATH=PICO8_ROOT_PATH
        elif (system.name == "voxatron"):
            LD_LIB="LD_LIBRARY_PATH=$LD_LIBRARY_PATH:"+str(BIOS / "voxatron")
            BIN_PATH=VOX_BIN_PATH
            CONTROLLERS=VOX_CONTROLLERS
            ROOT_PATH=VOX_ROOT_PATH
        else:
            raise BatoceraException(f"The Lexaloffle generator has been called for an unknwon system: {system.name}.")

        if not BIN_PATH.exists():
            raise BatoceraException(f"Lexaloffle official binary not found at {BIN_PATH}")

        if not os.access(BIN_PATH, os.X_OK):
            raise BatoceraException(f"{BIN_PATH} is not set as executable")

        # the command to run
        commandArray: list[str | Path] = [LD_LIB]
        commandArray.extend([BIN_PATH])
        commandArray.extend(["-desktop", SCREENSHOTS])  # screenshots
        commandArray.extend(["-windowed", "0"])                     # full screen
        # Display FPS
        if system.config.show_fps:
                commandArray.extend(["-show_fps", "1"])
        else:
                commandArray.extend(["-show_fps", "0"])

        rombase = rom.stem

        # .m3u support for multi-cart pico-8
        if rom.suffix.lower() == ".m3u":
            with rom.open() as fpin:
                lines = fpin.readlines()
            fullpath = rom.absolute().parent / lines[0].strip()
            commandArray.extend(["-root_path", fullpath.parent])
            rom = fullpath
        else:
            commandArray.extend(["-root_path", ROOT_PATH]) # store carts from splore

        if (rombase.lower() == "splore" or rombase.lower() == "console"):
            commandArray.extend(["-splore"])
        else:
            commandArray.extend(["-run", rom])

        controllersconfig = generate_sdl_game_controller_config(playersControllers)
        with ensure_parents_and_open(CONTROLLERS, "w") as file:
               file.write(controllersconfig)

        return Command.Command(array=commandArray, env={})

    def getInGameRatio(self, config, gameResolution, rom):
        return 4/3
