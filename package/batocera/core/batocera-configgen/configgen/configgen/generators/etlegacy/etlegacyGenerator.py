from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, ROMS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


class ETLegacyGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "etlegacy",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_ESC", "pause": "KEY_ESC" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        etLegacyDir = ROMS / "etlegacy" / "legacy"
        etLegacyFile = "legacy_2.82-dirty.pk3"
        etLegacySource = Path("/usr/share/etlegacy") / etLegacyFile
        etLegacyDest = etLegacyDir / etLegacyFile

        ## Configuration

        # Config file path
        config_dir = CONFIGS / "etlegacy" / "legacy"
        config_file_path = config_dir / "etconfig.cfg"

        mkdir_if_not_exists(config_dir)

        # Define the options to add or modify
        options_to_set = {
            "seta r_mode": "-1",
            "seta r_fullscreen": "1",
            "seta r_allowResize": "0",
            "seta r_centerWindow": "1",
            "seta r_customheight": f'"{gameResolution["height"]}"',
            "seta r_customwidth": f'"{gameResolution["width"]}"'
        }

        # Set language
        if system.isOptSet("etlegacy_language"):
            options_to_set["seta cl_lang"] = system.config["etlegacy_language"]
            options_to_set["seta ui_cl_lang"] = system.config["etlegacy_language"]
        else:
            options_to_set["seta cl_lang"] = "en"
            options_to_set["seta ui_cl_lang"] = "en"

        # Check if the file exists
        if config_file_path.is_file():
            with config_file_path.open('r') as config_file:
                lines = config_file.readlines()

            # Loop through the options and update the lines
            for key, value in options_to_set.items():
                option_exists = any(key in line for line in lines)
                if not option_exists:
                    lines.append(f"{key} \"{value}\"\n")
                else:
                    for i, line in enumerate(lines):
                        if key in line:
                            lines[i] = f"{key} \"{value}\"\n"

            # Write the modified content back to the file
            with config_file_path.open('w') as config_file:
                config_file.writelines(lines)
        else:
            # File doesn't exist, create it and add the options
            with config_file_path.open('w') as config_file:
                for key, value in options_to_set.items():
                    config_file.write(f"{key} \"{value}\"\n")

        # copy mod files needed
        mkdir_if_not_exists(etLegacyDir)

        # copy latest mod file to the rom directory
        if not etLegacyDest.exists():
            shutil.copy(etLegacySource, etLegacyDest)
        else:
            if etLegacySource.stat().st_mtime > etLegacyDest.stat().st_mtime:
                shutil.copy(etLegacySource, etLegacyDest)

        commandArray = ["etl"]

        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers)
            }
        )

    # Show mouse for menu / play actions
    def getMouseMode(self, config, rom):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
