from __future__ import annotations

from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from pathlib import Path

    from ...types import HotkeysContext


class X16emuGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "x16emu",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # set the file system path
        romdir = rom.parent

        # default options
        commandArray: list[str | Path] = [
            "x16emu",
            "-rom", "/userdata/bios/commanderx16/rom.bin", # bios
            "-fsroot", romdir, # file system
            "-ram", "2048", # specify 2MB of RAM by default
            "-rtc", # realtime clock
        ]

        # Check the rom extension to determine the appropriate option
        if rom.suffix == ".img":
            # Load the SD card
            commandArray.extend(["-sdcard", rom])
        elif rom.suffix == ".bas":
            # Load the BASIC program
            commandArray.extend(["-bas", rom])
        else:
            commandArray.extend(["-prg", rom, "-run"]) # use -prg for other files and run the program

        # If an autorun.cmd file exists in the same directory, add it to the command array
        autorun_cmd = romdir / "autorun.cmd"
        if autorun_cmd.exists():
            commandArray.extend(["-bas", autorun_cmd])

        commandArray.extend(["-scale", system.config.get("x16emu_scale", "2")])  # 2 = 1280 x 960

        if quality := system.config.get("x16emu_quality"):
            commandArray.extend(["-quality", quality])

        if system.config.get("x16emu_ratio") == "16:9":
            commandArray.extend(["-widescreen"])

        # Now add Controllers
        for nplayer, _ in enumerate(playersControllers[:4], start=1):
            commandArray.extend([f"-joy{nplayer}"])

        return Command.Command(
            array=commandArray,
            env={
                "XDG_DATA_HOME": CONFIGS,
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if config.get("x16emu_ratio") == "16:9":
            return 16/9
        return 4/3
