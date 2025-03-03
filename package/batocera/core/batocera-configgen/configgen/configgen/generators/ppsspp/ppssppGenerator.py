from __future__ import annotations

from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, SAVES
from ...controller import Controller, generate_sdl_game_controller_config
from ..Generator import Generator
from . import ppssppConfig, ppssppControllers
from .ppssppPaths import PPSSPP_CONFIG_DIR

if TYPE_CHECKING:
    from ...types import HotkeysContext, Resolution


class PPSSPPGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "ppsspp",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_F9", "pause": "KEY_F9", "rewind": "KEY_F1", "fastforward": "KEY_F2",
                      "next_slot": "KEY_F6", "previous_slot": "KEY_F5", "save_state": "KEY_F3", "restore_state": "KEY_F4" }
        }

    # Main entry of the module
    # Configure fba and return a command
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        ppssppConfig.writePPSSPPConfig(system)

        # Remove the old gamecontrollerdb.txt file
        dbpath = PPSSPP_CONFIG_DIR / "gamecontrollerdb.txt"
        if dbpath.exists():
            dbpath.unlink()

        # Generate the controls.ini
        if controller := Controller.find_player_number(playersControllers, 1):
            ppssppControllers.generateControllerConfig(controller)

        # The command to run
        commandArray = ['/usr/bin/PPSSPP', rom, '--fullscreen']

        # Adapt the menu size to low defenition
        # I've played with this option on PC to fix menu size in Hi-Resolution and it not working fine. I'm almost sure this option break the emulator (Darknior)
        if PPSSPPGenerator.isLowResolution(gameResolution):
            commandArray.extend(["--dpi", "0.5"])

        # state_slot option
        if system.isOptSet('state_filename'):
            commandArray.append(f"--state={system.config['state_filename']}")

        return Command.Command(
            array=commandArray,
            env={
                "XDG_CONFIG_HOME":CONFIGS,
                "XDG_DATA_HOME":SAVES,
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers, ignore_buttons = ["hotkey"]) # the hotkey button is used to open the menu
            }
        )

    @staticmethod
    def isLowResolution(gameResolution: Resolution):
        return gameResolution["width"] <= 480 or gameResolution["height"] <= 480

    # Show mouse on screen for the Config Screen
    def getMouseMode(self, config, rom):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
