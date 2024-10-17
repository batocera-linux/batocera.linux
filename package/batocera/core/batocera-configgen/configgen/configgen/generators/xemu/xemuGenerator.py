from __future__ import annotations

from shutil import copyfile
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator
from . import xemuConfig
from .xemuPaths import XEMU_BIN, XEMU_CONFIG, XEMU_SAVES

if TYPE_CHECKING:
    from pathlib import Path

    from ...types import HotkeysContext


class XemuGenerator(Generator):

    # Main entry of the module
    # Configure fba and return a command
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        xemuConfig.writeIniFile(system, rom, playersControllers, gameResolution)

        # copy the hdd if it doesn't exist
        if not (XEMU_SAVES / "xbox_hdd.qcow2").exists():
            mkdir_if_not_exists(XEMU_SAVES)
            copyfile("/usr/share/xemu/data/xbox_hdd.qcow2", XEMU_SAVES / "xbox_hdd.qcow2")

        # the command to run
        commandArray: list[str | Path] = [XEMU_BIN]
        commandArray.extend(["-config_path", XEMU_CONFIG])

        environment = {
            "XDG_CONFIG_HOME": CONFIGS,
            "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers)
        }

        return Command.Command(array=commandArray, env=environment)

    def getInGameRatio(self, config, gameResolution, rom):
        if ("xemu_scaling" in config and config["xemu_scaling"] == "stretch") or ("xemu_aspect" in config and config["xemu_aspect"] == "16x9"):
            return 16/9
        return 4/3

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "xemu",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }
