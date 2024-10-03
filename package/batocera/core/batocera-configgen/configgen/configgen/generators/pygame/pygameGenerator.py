from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


class PygameGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "pygame",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["pygame", rom]
        return Command.Command(array=commandArray)

    def executionDirectory(self, config, rom):
        return str(Path(rom).parent)

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
