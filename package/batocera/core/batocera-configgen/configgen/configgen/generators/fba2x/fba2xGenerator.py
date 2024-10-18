from __future__ import annotations

from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, LOGS, ensure_parents_and_open
from ...utils.configparser import CaseSensitiveConfigParser
from ..Generator import Generator
from . import fba2xConfig, fba2xControllers

if TYPE_CHECKING:
    from ...types import HotkeysContext

fbaRoot = CONFIGS / 'fba'
fbaCustom = fbaRoot / 'fba2x.cfg'

class Fba2xGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "fba2x",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        iniConfig = CaseSensitiveConfigParser()
        if fbaCustom.exists():
            iniConfig.read(fbaCustom)

        fba2xConfig.updateFBAConfig(iniConfig, system)
        fba2xControllers.updateControllersConfig(iniConfig, rom, playersControllers)

        # save the ini file
        with ensure_parents_and_open(fbaCustom, 'w') as configfile:
            iniConfig.write(configfile)

        commandArray = ['/usr/bin/fba2x', "--configfile", fbaCustom, '--logfile', LOGS / "fba2x.log"]
        commandArray.append(rom)
        return Command.Command(array=commandArray)
