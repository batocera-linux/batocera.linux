from __future__ import annotations

from typing import TYPE_CHECKING

from ... import Command
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

class SteamGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, esmetadata, guns, wheels, gameResolution):
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
        return Command.Command(array=commandArray)

    def getMouseMode(self, config, rom):
        return True

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "steam",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }
