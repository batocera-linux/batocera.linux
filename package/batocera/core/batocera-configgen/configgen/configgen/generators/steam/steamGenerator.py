from __future__ import annotations

from typing import TYPE_CHECKING

from ... import Command
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

class SteamGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        basename = rom.name
        gameId = None
        if basename != "Steam.steam":
            # read the id inside the file
            with rom.open() as f:
                gameId = str.strip(f.read())

        if gameId is None:
            commandArray = ["batocera-steam"]
        else:
            commandArray = ["batocera-steam", gameId]

        # Fix for Xbox Bluetooth controllers not working with Steam (issue #12731)
        # xpadneo fixes mappings at evdev level, but Steam reads raw HIDAPI data
        env = {"SDL_JOYSTICK_HIDAPI_XBOX": "0"}

        return Command.Command(array=commandArray, env=env)

    def getMouseMode(self, config, rom):
        return True

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "steam",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }
