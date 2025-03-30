from __future__ import annotations

from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import BIOS
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


class TsugaruGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # Start emulator fullscreen
        commandArray = ["/usr/bin/Tsugaru_CUI", BIOS / "fmtowns"]
        commandArray += ["-AUTOSCALE", "-HIGHRES", "-NOWAITBOOT"]
        commandArray += ["-GAMEPORT0", "KEY"]
        commandArray += ["-KEYBOARD", "DIRECT"]
        commandArray += ["-PAUSEKEY", "F10"]

        # CD Speed
        if (cdrom_speed := system.config.get('cdrom_speed', 'auto')) != 'auto':
            commandArray += ["-CDSPEED", cdrom_speed]

        # CPU Emulation
        if system.config.get('386dx') == '1':
            commandArray += ["-PRETEND386DX"]

        if rom.suffix.lower() in ['.iso', '.cue', '.bin']:
            # Launch CD-ROM
            commandArray += ["-CD", rom]
        else:
            # Launch floppy
            commandArray += ["-FD0", rom]

        return Command.Command(array=commandArray)

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "tsugaru",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_F10", "pause": "KEY_F10" }
        }
