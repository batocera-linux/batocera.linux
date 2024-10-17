from __future__ import annotations

import logging
from typing import Final

from ... import Command
from ...batoceraPaths import CONFIGS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ...settings.unixSettings import UnixSettings
from ..Generator import Generator

eslog = logging.getLogger(__name__)

_CONFIG_DIR: Final = CONFIGS / 'applewin'
_CONFIG_FILE: Final = _CONFIG_DIR / 'config.txt'

class AppleWinGenerator(Generator):
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        mkdir_if_not_exists(_CONFIG_DIR)

        config = UnixSettings(_CONFIG_FILE, separator=' ')

        config.write()
        commandArray = ["applewin" ]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers)
            })
