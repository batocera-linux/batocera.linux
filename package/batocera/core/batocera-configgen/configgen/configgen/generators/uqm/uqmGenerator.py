from __future__ import annotations

from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import ROMS, SAVES, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

_UQM_SAVES: Final = SAVES / 'uqm'
_UQM_ROMS: Final = ROMS / 'uqm'


class UqmGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "uqm",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        directories = [
            _UQM_SAVES / 'teams',
            _UQM_SAVES / 'save',
        ]

        for directory in directories:
            mkdir_if_not_exists(directory)

        with (_UQM_ROMS / 'version').open('a'): # Create file if does not exist
            pass

        commandArray = ["urquan",f"--contentdir={_UQM_ROMS}",
                        f"--configdir={_UQM_SAVES}"]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers)
            })
