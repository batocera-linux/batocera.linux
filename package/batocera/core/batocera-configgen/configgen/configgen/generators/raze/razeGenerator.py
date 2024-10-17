from __future__ import annotations

import logging
import platform
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, SAVES, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ...utils.buildargs import parse_args
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

eslog = logging.getLogger(__name__)

class RazeGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "raze",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "save_state": "KEY_F6", "restore_state": "KEY_F9" }
        }

    config_dir = CONFIGS / "raze"
    saves_dir = SAVES / "raze"
    # The main config file, which is emitted with duplicate keys and makes working with ConfigParser very annoying
    config_file = config_dir / "raze.ini"
    # A script file with console commands that are always ran when a game starts
    script_file = config_dir / "raze.cfg"
    # Names that Raze uses for game series specific sections in the config file
    game_names = [
        "Blood",
        "Duke",
        "Exhumed",
        "Nam",
        "Redneck",
        "ShadowWarrior",
        "WW2GI",
    ]
    # Options for config file that has more sensible controls and defaults, but only on first boot so overrides persist
    # Raze does not support global bindings; set defaults for each game series
    config_defaults = {}
    for name in game_names:
        config_defaults[f"{name}.ConsoleVariables"] = {
            "hud_size": 8,  # fullscreen / minimal HUD
            "m_sensitivity_x": 6.0,  # speed up movement and look slightly; its a bit slow as default
            "m_sensitivity_y": 5.5,
        }
        # ESC cannot be rebound, which is fine, we override in raze.keys
        config_defaults[f"{name}.Bindings"] = {
            "F6": "quicksave",  # F-keys accessed via raze.keys bindings
            "F9": "quickload",
            "F12": "screenshot",
            "C": "toggleconsole",  # useful for debugging and testing
            "Tab": "togglemap",
            "E": "+Move_Forward",
            "D": "+Move_Backward",
            "S": "+Strafe_Left",
            "F": "+Strafe_Right",
            "PgUp": "+Quick_Kick",  # used in several games
            "PgDn": "+Alt_Fire",  # used in Blood
            "End": "+Crouch",
            "Home": "+Fire",
            "Del": "toggle cl_autorun",
            "Ins": "+toggle_crouch",
            "UpArrow": "weapprev",
            "DownArrow": "weapnext",
            "LeftArrow": "invprev",
            "RightArrow": "invnext",
            "X": "invuse",
            "B": "+jump",
            "Y": "+open",
            "A": "+open",
        }
        config_defaults[f"{name}.AutomapBindings"] = {
            "PgUp": "+Shrink_Screen",
            "PgDn": "+Enlarge_Screen",
            "UpArrow": "+am_panup",
            "DownArrow": "+am_pandown",
            "LeftArrow": "+am_panleft",
            "RightArrow": "+am_panright",
            "Del": "togglefollow",
            "Ins": "togglerotate",
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        architecture = get_cpu_architecture()
        eslog.debug(f"*** Detected architecture is: {architecture} ***")

        mkdir_if_not_exists(self.config_dir)
        mkdir_if_not_exists(self.saves_dir)

        if not self.config_file.exists():
            with self.config_file.open("w") as config:
                for section in self.config_defaults:
                    config.write(f"[{section}]\n")
                    for key, value in self.config_defaults[section].items():
                        config.write(f"{key}={value}\n")
                    config.write("\n")

        config_backup = None
        if self.config_file.exists():
            with self.config_file.open("r") as original_file:
                config_backup = original_file.readlines()

        with self.config_file.open("w") as config_file:
            global_settings_found = False
            modified_global_settings = False
            for line in config_backup:
                # Check for the [GlobalSettings] section
                if line.strip() == "[GlobalSettings]":
                    global_settings_found = True

                # Modify options in the [GlobalSettings] section
                if global_settings_found:
                    # always set gl_es to true for arm
                    if line.strip().startswith("gl_es="):
                        if system.isOptSet("raze_api") and system.config["raze_api"] != "2":
                            if system.isOptSet("raze_api") and system.config["raze_api"] == "0":
                                if architecture in ["x86_64", "amd64", "i686", "i386"]:
                                    line = "gl_es=false\n"
                                else:
                                    eslog.debug(f"*** Architecture isn't intel it's: {architecture} therefore es is true ***")
                                    line = "gl_es=true\n"
                        else:
                            line = "gl_es=true\n"
                        modified_global_settings = True
                    elif line.strip().startswith("vid_preferbackend="):
                        if system.isOptSet("raze_api"):
                            line = f"vid_preferbackend={system.config['raze_api']}\n"
                            modified_global_settings = True
                        else:
                            line = "vid_preferbackend=2\n"

                # Write the line
                config_file.write(line)

            # If [GlobalSettings] was not found, add it with the modified options
            if not global_settings_found:
                eslog.debug("Global Settings NOT found")
                config_file.write("[GlobalSettings]\n")
                if system.isOptSet("raze_api") and system.config["raze_api"] != "2":
                    if system.isOptSet("raze_api") and system.config["raze_api"] == "0":
                        if architecture in ["x86_64", "amd64", "i686", "i386"]:
                            line = "gl_es=false\n"
                        else:
                            eslog.debug(f"*** Architecture isn't intel it's: {architecture} therefore es is true ***")
                            line = "gl_es=true\n"
                if system.isOptSet("raze_api"):
                    config_file.write(f"vid_preferbackend={system.config['raze_api']}\n")
                else:
                    config_file.write("vid_preferbackend=2\n")
                modified_global_settings = True

        with self.script_file.open("w") as script:
            script.write(
                "# This file is automatically generated by razeGenerator.py\n"
                f"vid_fps {'true' if system.getOptBoolean('showFPS') else 'false'}\n"
                "echo BATOCERA\n"  # easy check that script ran in console
            )

        # Launch arguments
        launch_args: list[str | Path] = ["raze"]
        result = parse_args(launch_args, Path(rom))
        if not result.okay:
            raise Exception(result.message)

        launch_args += [
            "-exec", self.script_file,
            # Disable controllers because support is poor; we use evmapy instead
            "-nojoy",
            "-width", str(gameResolution["width"]),
            "-height", str(gameResolution["height"]),
            "-nologo" if system.getOptBoolean("nologo") else "",
        ]

        return Command.Command(
            array=launch_args,
            env={
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers)
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9

def get_cpu_architecture():
    return platform.uname().machine
