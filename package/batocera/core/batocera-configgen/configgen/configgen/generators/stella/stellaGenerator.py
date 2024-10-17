from __future__ import annotations

import logging

from ... import Command
from ...controller import generateSdlGameControllerConfig
from ..Generator import Generator

eslog = logging.getLogger(__name__)

class StellaGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Launch Stella
        commandArray = ["stella " , rom ]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': generateSdlGameControllerConfig(playersControllers)
            }
        )
