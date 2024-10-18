from __future__ import annotations

from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import ensure_parents_and_open, mkdir_if_not_exists
from ...utils.configparser import CaseSensitiveConfigParser
from ..Generator import Generator
from . import mupenConfig, mupenControllers
from .mupenPaths import MUPEN_CONFIG_DIR, MUPEN_CUSTOM

if TYPE_CHECKING:
    from pathlib import Path

    from ...types import HotkeysContext


class MupenGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "mupen64",
            "keys": { "exit": "KEY_ESC", "save_state": "KEY_F5", "restore_state": "KEY_F7", "menu": "KEY_P", "pause": "KEY_P" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # Read the configuration file
        iniConfig = CaseSensitiveConfigParser(interpolation=None)
        if MUPEN_CUSTOM.exists():
            iniConfig.read(MUPEN_CUSTOM)
        else:
            mkdir_if_not_exists(MUPEN_CUSTOM.parent)
            iniConfig.read(MUPEN_CUSTOM)

        mupenConfig.setMupenConfig(iniConfig, system, playersControllers, gameResolution)
        mupenControllers.setControllersConfig(iniConfig, playersControllers, system, wheels)

        # Save the ini file
        with ensure_parents_and_open(MUPEN_CUSTOM, 'w') as configfile:
            iniConfig.write(configfile)

        # Command
        commandArray: list[str | Path] = ['/usr/bin/mupen64plus', "--corelib", "/usr/lib/libmupen64plus.so.2.0.0", "--gfx", "/usr/lib/mupen64plus/mupen64plus-video-{}.so".format(system.config['core']), "--configdir", MUPEN_CONFIG_DIR, "--datadir", MUPEN_CONFIG_DIR]

        # state_filename option
        if system.isOptSet('state_filename'):
            commandArray.extend(["--savestate", system.config['state_filename']])

        commandArray.append(rom)

        return Command.Command(array=commandArray)

    def getInGameRatio(self, config, gameResolution, rom):
        if ("mupen64plus_ratio" in config and config["mupen64plus_ratio"] == "16/9") or ("mupen64plus_ratio" not in config and "ratio" in config and config["ratio"] == "16/9"):
            return 16/9
        return 4/3
