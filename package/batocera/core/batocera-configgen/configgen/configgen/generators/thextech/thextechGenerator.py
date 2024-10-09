from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import SAVES, mkdir_if_not_exists
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

eslog = logging.getLogger(__name__)

_THEXTECH_SAVES: Final = SAVES / "thextech"

class TheXTechGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        mkdir_if_not_exists(_THEXTECH_SAVES)

        commandArray = ["/usr/bin/thextech", "-u", _THEXTECH_SAVES]

        # rendering_mode: sw, hw (default), vsync
        if system.isOptSet('rendering_mode'):
            commandArray.extend(["-r", system.config['rendering_mode']])

        if system.isOptSet('frameskip') and system.getOptBoolean('frameskip') == False:
            commandArray.extend(["--no-frameskip"])
        else:
            commandArray.extend(["--frameskip"])

        commandArray.extend(["-c", rom])

        return Command.Command(array=commandArray)

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "thextech",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_ENTER", "pause": "KEY_ENTER" }
        }
