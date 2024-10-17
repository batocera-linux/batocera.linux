from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


class ShGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "shell",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        rom_path = Path(rom)

        # in case of squashfs, the root directory is passed
        runsh = rom_path / "run.sh"
        shrom = runsh if runsh.exists() else rom_path

        commandArray = ["/bin/bash", shrom]
        return Command.Command(array=commandArray,env={
            "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers)
        })

    def getMouseMode(self, config, rom):
        return True
