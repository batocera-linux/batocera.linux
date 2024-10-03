from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


class DosBoxStagingGenerator(Generator):

    # Main entry of the module
    # Return command
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Find rom path
        gameDir = Path(rom)
        batFile = gameDir / "dosbox.bat"
        gameConfFile = gameDir / "dosbox.cfg"

        commandArray: list[str | Path] = [
            '/usr/bin/dosbox-staging',
            "-fullscreen",
            "-userconf",
            "-exit",
            batFile,
            "-c", f"""set ROOT={gameDir!s}"""
        ]
        if gameConfFile.is_file():
            commandArray.append("-conf")
            commandArray.append(gameConfFile)
        else:
            commandArray.append("-conf")
            commandArray.append(CONFIGS / 'dosbox' / 'dosbox.conf')

        return Command.Command(array=commandArray)

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "dosboxstaging",
            "keys": { "exit": ["KEY_LEFTCTRL", "KEY_F9"] }
        }
