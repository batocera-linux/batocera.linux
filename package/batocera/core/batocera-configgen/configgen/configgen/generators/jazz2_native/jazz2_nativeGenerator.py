from __future__ import annotations
from typing import TYPE_CHECKING, Final
from pathlib import Path

from ... import Command
from ...batoceraPaths import CONFIGS, CACHE
from ...controller import generate_sdl_game_controller_config, write_sdl_controller_db
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

class Jazz2_NativeGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "jazz2",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        dbfile = Path("/usr/share/jazz2/gamecontrollerdb.txt")
        write_sdl_controller_db(playersControllers, dbfile)

        commandArray = ["jazz2"]

        return Command.Command(
            array=commandArray,
            env={
                "XDG_CONFIG_HOME": CONFIGS,
                "XDG_CACHE_HOME": CACHE,
                "XDG_DATA_HOME": "/userdata/roms/jazz2",
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9
