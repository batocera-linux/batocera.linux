from __future__ import annotations

from ... import Command
from ...controller import generateSdlGameControllerConfig
from ..Generator import Generator


class EtekwarGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["etekwar", rom]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': generateSdlGameControllerConfig(playersControllers)
            })
