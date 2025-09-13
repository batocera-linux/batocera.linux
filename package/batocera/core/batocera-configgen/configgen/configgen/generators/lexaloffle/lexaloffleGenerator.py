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


# Generator for the official pico8 / voxatron binaries from Lexaloffle
class LexaloffleGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "lexaloffle",
            "keys": {
                "exit": ["KEY_LEFTCTRL", "KEY_Q"],
                "menu": "KEY_ENTER",
                "reset": ["KEY_LEFTCTRL", "KEY_R"],
            },
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Select system-specific paths
        if system.name == "pico8":
            lib_dir = BIOS / "pico-8"
            BIN_PATH = PICO8_BIN_PATH
            CONTROLLERS = PICO8_CONTROLLERS
            ROOT_PATH = PICO8_ROOT_PATH
        elif system.name == "voxatron":
            lib_dir = BIOS / "voxatron"
            BIN_PATH = VOX_BIN_PATH
            CONTROLLERS = VOX_CONTROLLERS
            ROOT_PATH = VOX_ROOT_PATH
        else:
            raise BatoceraException(
                f"The Lexaloffle generator has been called for an unknown system: {system.name}."
            )

        # Sanity checks
        if not BIN_PATH.exists():
            raise BatoceraException(f"Lexaloffle official binary not found at {BIN_PATH}")

        if not os.access(BIN_PATH, os.X_OK):
            raise BatoceraException(f"{BIN_PATH} is not set as executable")

        # Build command (first element MUST be the binary)
        commandArray: list[str] = [str(BIN_PATH)]
        commandArray.extend(["-desktop", str(SCREENSHOTS)])  # screenshots output dir
        commandArray.extend(["-windowed", "0"])              # fullscreen
        commandArray.extend(["-show_fps", "1" if system.config.show_fps else "0"])

        rombase = rom.stem

        # .m3u support for multi-cart pico-8
        if rom.suffix.lower() == ".m3u":
            with rom.open() as fpin:
                lines = fpin.readlines()
            fullpath = rom.absolute().parent / lines[0].strip()
            commandArray.extend(["-root_path", str(fullpath.parent)])
            rom = fullpath
        else:
            # default root path where Splore stores carts, etc.
            commandArray.extend(["-root_path", str(ROOT_PATH)])

        # Splore / console vs direct run
        if rombase.lower() in ("splore", "console"):
            commandArray.extend(["-splore"])
        else:
            commandArray.extend(["-run", str(rom)])

        # Controllers config (SDL game controller DB format)
        controllersconfig = generate_sdl_game_controller_config(playersControllers)
        with ensure_parents_and_open(CONTROLLERS, "w") as file:
            file.write(controllersconfig)

        # Prepare environment: merge LD_LIBRARY_PATH
        env: dict[str, str] = {}
        existing = os.environ.get("LD_LIBRARY_PATH", "")
        env["LD_LIBRARY_PATH"] = f"{existing}:{lib_dir}" if existing else str(lib_dir)

        return Command.Command(array=commandArray, env=env)


    def getInGameRatio(self, config, gameResolution, rom):
        # Try to retrieve the system name from config
        sysname = None
        try:
            if "system" in config and isinstance(config["system"], dict):
                sysname = config["system"].get("name")
            elif "system.name" in config:
                sysname = config.get("system.name")
        except Exception:
            pass

        # PICO-8 runs in a square 1:1 aspect ratio
        if sysname == "pico8":
            return 1.0
        # Voxatron runs in a classic 4:3 aspect ratio
        elif sysname == "voxatron":
            return 4/3
        # Default fallback
        return 4/3

