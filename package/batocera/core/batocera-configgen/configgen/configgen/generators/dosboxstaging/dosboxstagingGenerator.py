from __future__ import annotations

from typing import TYPE_CHECKING

from ... import Command
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

class DosBoxStagingGenerator(Generator):

    # Main entry of the module
    # Return command
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Find rom path
        batFile = rom / "dosbox.bat"
        gameConfFile_cfg = rom / "dosbox.cfg"
        gameConfFile_conf = rom / "dosbox.conf"

        commandArray = [
            '/usr/bin/dosbox-staging',
            "-fullscreen",
            "-userconf",
            "-exit",
        ]

        # Append the batch file to execute
        if batFile.is_file():
            commandArray.append(batFile)

        commandArray.extend(["-c", f"""set ROOT={rom!s}"""])

        # Determine which config file to use
        configFileToUse = None
        if gameConfFile_cfg.is_file():
            configFileToUse = gameConfFile_cfg
        elif gameConfFile_conf.is_file():
            configFileToUse = gameConfFile_conf

        # Append the specific game config file if found
        if configFileToUse is not None:
            commandArray.extend(["-conf", str(configFileToUse)])

        return Command.Command(array=commandArray)

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "dosboxstaging",
            "keys": { "exit": ["KEY_LEFTCTRL", "KEY_F9"] }
        }
