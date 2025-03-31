from __future__ import annotations

from typing import TYPE_CHECKING

from ... import Command
from ..Generator import Generator
from . import kodiConfig

if TYPE_CHECKING:
    from ...types import HotkeysContext


class KodiGenerator(Generator):

    # Main entry of the module
    # Configure kodi inputs and return the command to run
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        kodiConfig.writeKodiConfig(playersControllers)
        commandArray = ['/usr/bin/batocera-kodilauncher']
        return Command.Command(array=commandArray)

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "kodi",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }
