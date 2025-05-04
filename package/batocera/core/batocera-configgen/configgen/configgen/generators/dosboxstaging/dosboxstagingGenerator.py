from __future__ import annotations

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
        batFile = rom / "dosbox.bat"
        gameConfFile = rom / "dosbox-staging.conf"

        commandArray = [
            '/usr/bin/dosbox-staging',
            "-fullscreen",
            "-userconf",
            "-exit",
            batFile,
            "-c", f"""set ROOT={rom!s}"""
        ]
        if gameConfFile.is_file():
            commandArray.append("-conf")
            commandArray.append(gameConfFile)

        return Command.Command(array=commandArray)

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "dosboxstaging",
            "keys": { "exit": ["KEY_LEFTCTRL", "KEY_F9"] }
        }
