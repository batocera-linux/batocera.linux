from __future__ import annotations

from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import SAVES, mkdir_if_not_exists
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

_THEXTECH_SAVES: Final = SAVES / "thextech"

class TheXTechGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, esmetadata, guns, wheels, gameResolution):

        mkdir_if_not_exists(_THEXTECH_SAVES)

        commandArray = ["/usr/bin/thextech", "-u", _THEXTECH_SAVES]

        # rendering_mode: sw, hw (default), vsync
        if rendering_mode := system.config.get('rendering_mode'):
            commandArray.extend(["-r", rendering_mode])

        commandArray.extend([system.config.get_bool('frameskip', True, return_values=("--frameskip", "--no-frameskip"))])

        commandArray.extend(["-c", rom])

        return Command.Command(array=commandArray)

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "thextech",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_ENTER", "pause": "KEY_ENTER" }
        }
