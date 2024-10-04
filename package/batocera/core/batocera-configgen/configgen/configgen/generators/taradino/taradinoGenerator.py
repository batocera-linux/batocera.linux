from __future__ import annotations

from typing import TYPE_CHECKING

from ... import Command, controllersConfig
from ...batoceraPaths import CONFIGS
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


class TaradinoGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "taradino",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        commandArray = [ "taradino" ]

        return Command.Command(
            array=commandArray,
            env={
                "XDG_DATA_HOME": CONFIGS,
                "XDG_DATA_DIRS": "/userdata/roms/rott",
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )
