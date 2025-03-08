from __future__ import annotations

from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import ROMS
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

vkquakeRomPath = ROMS / "quake"

class VKQuakeGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "vkquake",
            "keys": { "exit": "KEY_F10", "save_state": "KEY_F6", "restore_state": "KEY_F9" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        romName = rom.name

        commandArray = ['/usr/bin/vkquake', '-basedir', str(vkquakeRomPath)]

        if "scourge" in romName.lower():
            commandArray.extend(["-hipnotic"])
        if "dissolution" in romName.lower():
            commandArray.extend(["-rogue"])

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
