from __future__ import annotations

import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import CONFIGS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator
from . import viceConfig, viceControllers

if TYPE_CHECKING:
    from ...types import HotkeysContext

_VICE_CONFIG_DIR: Final = CONFIGS / 'vice'

class ViceGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "vice",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def getResolutionMode(self, config):
        return 'default'

    # Main entry of the module
    # Return command
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        mkdir_if_not_exists(_VICE_CONFIG_DIR)

        # configuration file
        viceConfig.setViceConfig(_VICE_CONFIG_DIR, system, metadata, guns, rom)

        # controller configuration
        viceControllers.generateControllerConfig(system, _VICE_CONFIG_DIR, playersControllers)

        commandArray = [Path('/usr/bin') / system.config['core']]
        # Determine the way to launch roms based on extension type
        rom_extension = Path(rom).suffix.lower()
        # determine extension if a zip file
        if rom_extension == ".zip":
            with zipfile.ZipFile(rom, "r") as zip_file:
                for zip_info in zip_file.infolist():
                    rom_extension = Path(zip_info.filename).suffix

        # TODO - add some logic for various extension types

        commandArray.append(rom)

        return Command.Command(
            array=commandArray,
            env={
                "XDG_CONFIG_HOME": CONFIGS,
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )
