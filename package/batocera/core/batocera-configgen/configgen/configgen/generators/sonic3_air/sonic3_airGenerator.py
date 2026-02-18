from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import CONFIGS, SAVES, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

SYSTEM_DIR: Final = Path('/usr/bin/sonic3-air')
SAVES_DIR: Final = SAVES / "sonic3-air"
CONFIG_DIR: Final = CONFIGS / "Sonic3AIR"

class Sonic3AIRGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "sonic3_air",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "save_state": "KEY_F5", "restore_state": "KEY_F8" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        config_file = SYSTEM_DIR / "config.json"
        oxygen_file = SYSTEM_DIR / "oxygenproject.json"
        config_dest_file = CONFIG_DIR / "config.json"
        oxygen_dest_file = CONFIG_DIR / "oxygenproject.json"
        settings_file = CONFIG_DIR / "settings.json"

        ## Configuration

        # copy configuration json files so we can manipulate them
        mkdir_if_not_exists(CONFIG_DIR)
        if not config_dest_file.exists():
            shutil.copy(config_file, config_dest_file)
        if not oxygen_dest_file.exists():
            shutil.copy(oxygen_file, oxygen_dest_file)

        # saves dir
        mkdir_if_not_exists(SAVES_DIR)

        # read the json file
        # can't use `import json` as the file is not compliant
        with config_dest_file.open('r') as file:
            json_text = file.read()
        # update the "SaveStatesDir"
        json_text = json_text.replace('"SaveStatesDir":  "saves/states"', f'"SaveStatesDir":  "{SAVES_DIR}"')

        # extract the current resolution value
        current_resolution = json_text.split('"WindowSize": "')[1].split('"')[0]
        # replace the resolution with new values
        new_resolution = f'{gameResolution["width"]} x {gameResolution["height"]}'
        json_text = json_text.replace(f'"WindowSize": "{current_resolution}"', f'"WindowSize": "{new_resolution}"')

        with config_dest_file.open('w') as file:
            file.write(json_text)

        # settings json - compliant
        # ensure fullscreen
        if settings_file.exists():
            with settings_file.open('r') as file:
                settings_data = json.load(file)
                settings_data["Fullscreen"] = 1
        else:
            settings_data = {"Fullscreen": 1}

        with settings_file.open('w') as file:
            json.dump(settings_data, file, indent=4)

        # now run
        commandArray = [SYSTEM_DIR / "sonic3air_linux"]

        return Command.Command(
            array=commandArray,
            env={
                "XDG_DATA_HOME":CONFIGS,
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0",
                "SDL_AUDIODRIVER": "alsa"
            }
        )

    # Show mouse for menu / play actions
    def getMouseMode(self, config, rom):
        return False

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
