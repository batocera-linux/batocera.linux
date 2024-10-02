from __future__ import annotations

from typing import Final

from ... import Command, controllersConfig
from ...batoceraPaths import CONFIGS, mkdir_if_not_exists
from ...settings.unixSettings import UnixSettings
from ...utils.logger import get_logger
from ..Generator import Generator

eslog = get_logger(__name__)

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
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
