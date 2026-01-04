from __future__ import annotations

from typing import TYPE_CHECKING

from ... import Command
from ...controller import generate_sdl_game_controller_config, write_sdl_controller_db
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


class XroarGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "xroar",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        commandArray = ["xroar", "-rompath", "/userdata/bios:/userdata/bios/xroar", "-fs", "-default-machine", "coco2bus", rom]
        return Command.Command(array=commandArray)

    def getMouseMode(self, config, rom):
        return True
