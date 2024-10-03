from __future__ import annotations

import os

from ... import Command, controllersConfig
from ...batoceraPaths import ROMS
from ...utils.logger import get_logger
from ..Generator import Generator

eslog = get_logger(__name__)


class OpenJazzGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        try:
            os.chdir(ROMS / "openjazz")
        except:
            eslog.error("ERROR: Game assets not installed. You can get them from the Batocera Content Downloader.")
        commandArray = ["OpenJazz"]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
