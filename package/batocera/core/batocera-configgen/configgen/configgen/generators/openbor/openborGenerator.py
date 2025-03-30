from __future__ import annotations

import logging
import os
import re
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, ROMS, SAVES, mkdir_if_not_exists
from ...settings.unixSettings import UnixSettings
from ..Generator import Generator
from . import openborControllers

if TYPE_CHECKING:
    from pathlib import Path

    from ...types import HotkeysContext

_logger = logging.getLogger(__name__)

class OpenborGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "openbor",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    # Main entry of the module
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        configDir = CONFIGS / 'openbor'
        mkdir_if_not_exists(configDir)
        mkdir_if_not_exists(SAVES / 'openbor')

        # guess the version to run
        core = system.config.core
        if not system.config.core_forced:
            core = OpenborGenerator.guessCore(rom)
        _logger.debug("core taken is %s", core)

        # config file
        if core == "openbor4432":
            configfilename = "config4432.ini"
        elif core == "openbor6412":
            configfilename = "config6412.ini"
        elif core == "openbor7142":
            configfilename = "config7142.ini"
        elif core == "openbor7530":
            configfilename = "config7530.ini"
        else:
            configfilename = "config7530.ini"

        config = UnixSettings(configDir / configfilename, separator='')

        # general
        config.save("fullscreen", "1")
        config.save("usegl", "1")
        config.save("usejoy", "1")

        # options
        config.save("stretch", system.config.get("openbor_ratio", "0"))
        config.save("swfilter", system.config.get("openbor_filter", "0"))
        config.save("vsync", system.config.get("openbor_vsync", "1"))
        config.save("fpslimit", system.config.get("openbor_limit", "0"))

        # controllers
        openborControllers.generateControllerConfig(config, playersControllers, core)

        # rumble
        rumble = system.config.get("openbor_rumble", "0")
        config.save("joyrumble.0", rumble)
        config.save("joyrumble.1", rumble)
        config.save("joyrumble.2", rumble)
        config.save("joyrumble.3", rumble)

        config.write()

        # change directory for wider compatibility
        os.chdir(ROMS / "openbor")

        return OpenborGenerator.executeCore(core, rom)

    @staticmethod
    def executeCore(core: str, rom: Path) -> Command.Command:
        if core == "openbor4432":
            commandArray = ["OpenBOR4432", rom]
        elif core == "openbor6412":
            commandArray = ["OpenBOR6412", rom]
        elif core == "openbor7142":
            commandArray = ["OpenBOR7142", rom]
        elif core == "openbor7530":
            commandArray = ["OpenBOR7530", rom]
        else:
            commandArray = ["OpenBOR7530", rom]
        return Command.Command(array=commandArray)

    @staticmethod
    def guessCore(rom: Path) -> str:
        versionstr = re.search(r'\[.*([0-9]{4})\]+', rom.name)
        if versionstr is None:
            return "openbor7530"
        version = int(versionstr.group(1))

        if version < 6000:
            return "openbor4432"
        if version < 6500:
            return "openbor6412"
        if version < 7530:
            return "openbor7142"
        return "openbor7530"
