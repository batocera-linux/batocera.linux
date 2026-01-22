from __future__ import annotations

from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS
from ..Generator import Generator

if TYPE_CHECKING:
    from pathlib import Path

    from ...types import HotkeysContext

def _find_iname(directory: Path, filename: str) -> Path | None:
    if not directory.is_dir():
        return None

    lower_filename = filename.lower()
    return next((f for f in directory.iterdir()
                 if f.is_file() and f.name.lower() == lower_filename), None)


class DosBoxStagingGenerator(Generator):
    # Main entry of the module
    # Returns a populated Command object
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # DOSBox Staging common resource data and conf file
        common_resource_dir = CONFIGS / 'dosbox'
        common_resource_conf = _find_iname(common_resource_dir, "dosbox-staging.conf")

        dosbox_cfg =  _find_iname(rom, "dosbox.cfg")
        dosbox_conf = _find_iname(rom, "dosbox.conf")
        dosbox_bat = _find_iname(rom, "dosbox.bat")

        is_configured = dosbox_cfg or dosbox_conf or dosbox_bat

        commandArray = [
            '/usr/bin/dosbox-staging',
            "--fullscreen",
            "--working-dir", str(rom),
            "-c", f"set WORKDIR={rom}",
        ]

        if common_resource_dir.is_dir():
            commandArray.extend(["-c", f"set RESDIR={str(common_resource_dir)}"])

        if common_resource_conf:
            commandArray.extend(["-c", f"set RESCONF={str(common_resource_conf)}"])

        if dosbox_cfg:
            commandArray.extend(["--conf", dosbox_cfg.name, "-c", f"set GAMECFG={dosbox_cfg.name}"])
        elif dosbox_conf:
            commandArray.extend(["--conf", dosbox_conf.name, "-c", f"set GAMECONF={dosbox_conf.name}"])

        if dosbox_bat:
            commandArray.extend([dosbox_bat.name, "-c", f"set GAMEBAT={dosbox_bat.name}"])

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
                "-c", "@echo off",
                "-c", "mount c .",
                "-c", "c:"
            ])

        return Command.Command(array=commandArray)


    def getMouseMode(self, config, rom):
        return True


    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "dosboxstaging",
            "keys": { "exit": ["KEY_LEFTCTRL", "KEY_F9"] }
        }
