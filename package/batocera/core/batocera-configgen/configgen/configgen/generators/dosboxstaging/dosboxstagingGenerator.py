from __future__ import annotations

from typing import TYPE_CHECKING

from ... import Command
from ..Generator import Generator

if TYPE_CHECKING:
    from pathlib import Path

    from ...types import HotkeysContext

class DosBoxStagingGenerator(Generator):

    # Main entry of the module
    # Returns a populated Command object
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # Common arguments
        commandArray: list[Path | str] = [
            '/usr/bin/dosbox-staging',
            "--working-dir", f"""{rom!s}""",
            "--fullscreen"
        ]

        dosbox_cfg = rom / "dosbox.cfg"
        dosbox_conf = rom / "dosbox.conf"
        dosbox_bat = rom / "dosbox.bat"

        is_configured = False

        if dosbox_cfg.is_file():
            is_configured = True
            commandArray.extend(["-conf", dosbox_cfg.name])

        elif dosbox_conf.is_file():
            is_configured = True
            commandArray.extend(["-conf", dosbox_conf.name])

        if dosbox_bat.is_file():
            is_configured = True
            commandArray.extend([dosbox_bat.name])

        if is_configured:
           # If the game's configured, then we can disable the startup logos and
           # automatically exit when the game quits.
           #
           commandArray.extend([
               "--set", "startup_verbosity=quiet",
               "--exit"])
        else:
            # If the game's not configured, then place the user at a valid C:\>
            # prompt inside the game's root directory.
            #
            commandArray.extend([
                "-c", f"""set ROOT={rom!s}""",
                "-c", "@echo off",
                "-c", "mount c .",
                "-c", "c:"
            ])

        return Command.Command(array=commandArray)

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "dosboxstaging",
            "keys": { "exit": ["KEY_LEFTCTRL", "KEY_F9"] }
        }
