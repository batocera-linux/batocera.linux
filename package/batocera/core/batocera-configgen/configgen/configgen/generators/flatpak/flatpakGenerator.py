from __future__ import annotations

import os
from typing import TYPE_CHECKING

from ... import Command
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


class FlatpakGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, esmetadata, guns, wheels, gameResolution):

        romId = None
        with rom.open() as f:
            romId = str.strip(f.read())

        # bad hack in a first time to get audio for user batocera
        os.system('chown -R root:audio /var/run/pulse')
        os.system('chmod -R g+rwX /var/run/pulse')

        # the directory monitor must exist and all the dirs must be owned by batocera
        commandArray = ["/usr/bin/flatpak", "run", "-v", romId]
        return Command.Command(array=commandArray)

    def getMouseMode(self, config, rom):
        return True

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "flatpak",
            "keys": { "exit": "flatpak kill $(flatpak ps --columns=application | head -n 1)" }
        }
