#
# This file is part of the batocera distribution (https://batocera.org).
# Copyright (c) 2025+.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# YOU MUST KEEP THIS HEADER AS IT IS
#
from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, cast

import toml

from ... import Command
from ...batoceraPaths import CONFIGS, mkdir_if_not_exists
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

_logger = logging.getLogger(__name__)


class YmirGenerator(Generator):
    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "ymir",
            "keys": {
                "exit": "killall -9 ymir",
                "save_state": "KEY_F2",
                "restore_state": "KEY_F3"
            }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Set the paths using Path objects
        configPath = CONFIGS / "ymir"
        toml_file = configPath / "Ymir.toml"
        savesPath = Path("/userdata/saves/ymir")
        romDir = Path("/userdata/roms/saturn")
        iplDir = Path("/userdata/bios")

        mkdir_if_not_exists(configPath)
        mkdir_if_not_exists(savesPath)

        # Adjust the Ymir.toml file
        config: dict[str, dict[str, object]] = {}

        # Check if the file exists
        if toml_file.is_file():
            try:
                config = toml.loads(toml_file.read_text())
            except Exception as e:
                _logger.error("Failed to load existing ymir config: %s. Will create default.", e)

        # If config is empty, create default structure
        if not config:
            _logger.info("Creating default ymir config at %s", toml_file)
            config = {
                "General": {
                    "BoostEmuThreadPriority": True,
                    "BoostProcessPriority": True,
                    "EnableRewindBuffer": False,
                    "PauseWhenUnfocused": False,
                    "PreloadDiscImagesToRAM": False,
                    "RewindCompressionLevel": 12
                },
                "System": {
                    "AutoDetectRegion": True
                },
                "Video": {
                    "AutoResizeWindow": False,
                    "Deinterlace": False,
                    "FullScreen": True,
                    "ForceAspectRatio": True
                }
            }

        # --- Apply Batocera Specific Overrides ---

        # General
        general_config = config.setdefault("General", {})
        # adds [General.PathOverrides]
        path_overrides = cast("dict[str, str]", general_config.setdefault("PathOverrides", {}))

        # Set the path values.
        path_overrides["BackupMemory"] = ''
        path_overrides["Dumps"] = ''
        path_overrides["ExportedBackups"] = ''
        path_overrides["IPLROMImages"] = str(iplDir)
        path_overrides["PersistentState"] = ''
        path_overrides["ROMCartImages"] = str(romDir)
        path_overrides["SaveStates"] = str(savesPath)

        # Video
        video_config = config.setdefault("Video", {})
        video_config["AutoResizeWindow"] = False
        video_config["DisplayVideoOutputInWindow"] = False
        video_config["FullScreen"] = True
        video_config["ThreadedDeinterlacer"] = True
        video_config["ForceAspectRatio"] = True
        video_config["ForceIntegerScaling"] = False

        # Options
        video_config["ForcedAspect"] = system.config.get_float("ymir_aspect", 1.5)
        video_config["Deinterlace"] = system.config.get_bool("ymir_interlace", True)
        video_config["TransparentMeshes"] = system.config.get_bool("ymir_meshes", False)
        video_config["Rotation"] = system.config.get_str("ymir_rotation", "Normal")

        # Controllers
        input_config = config.setdefault("Input", {})
        input_config["GamepadAnalogToDigitalSensitivity"] = 0.20000000298023224
        input_config["GamepadLSDeadzone"] = 0.15000000596046448
        input_config["GamepadRSDeadzone"] = 0.15000000596046448

        # Clear existing port configurations for the 2 supported ports
        for i in range(1, 3):
            if f"Port{i}" in input_config:
                del input_config[f"Port{i}"]

        # Default keyboard binds for the AnalogPad profile
        default_keyboard_maps = {
            1: { # Player 1
                "A": ["J"], "B": ["K"], "C": ["L"],
                "X": ["U"], "Y": ["I"], "Z": ["O"],
                "L": ["Q"], "R": ["E"],
                "Up": ["W"], "Down": ["S"], "Left": ["A"], "Right": ["D"],
                "Start": ["F", "G", "H"],
                "SwitchMode": ["Ctrl+B"]
            },
            2: { # Player 2
                "A": ["KeyPad1"], "B": ["KeyPad2"], "C": ["KeyPad3"],
                "X": ["KeyPad4"], "Y": ["KeyPad5"], "Z": ["KeyPad6"],
                "L": ["Insert", "KeyPad7"], "R": ["PageUp", "KeyPad9"],
                "Up": ["Home", "Up"], "Down": ["End", "Down"], "Left": ["Delete", "Left"], "Right": ["PageDown", "Right"],
                "Start": ["KeyPadEnter"],
                "SwitchMode": ["KeyPadAdd"]
            }
        }

        # Mapping of Ymir's binds to SDL Gamepad suffixes
        ymir_sdl_map = {
            "A": "GamepadX",
            "B": "GamepadA",
            "C": "GamepadB",
            "X": "GamepadLeftBumper",
            "Y": "GamepadY",
            "Z": "GamepadRightBumper",
            "Start": "GamepadStart",
            "SwitchMode": "GamepadLeftThumb",
            "DPad": "GamepadDPad",
            "AnalogStick": "GamepadLeftStick",
            "AnalogL": "GamepadLeftTrigger",
            "AnalogR": "GamepadRightTrigger"
        }

        # Configure up to a maximum of two controllers
        for pad in playersControllers[:2]:
            port_key = f"Port{pad.player_number}"
            port_config = cast("dict[str, object]", input_config.setdefault(port_key, {}))
            port_config["PeripheralType"] = 'AnalogPad'

            port_config["DevicePath"] = pad.device_path

            analog_pad_config = cast("dict[str, object]", port_config.setdefault("AnalogPad", {}))
            binds_config = cast("dict[str, list[str]]", analog_pad_config.setdefault("Binds", {}))

            player_keyboard_map = default_keyboard_maps.get(pad.player_number, {})

            for key, val in player_keyboard_map.items():
                binds_config[key] = val.copy()

            for ymir_key, sdl_suffix in ymir_sdl_map.items():
                bind_list = binds_config.setdefault(ymir_key, [])
                bind_list.append(f'{sdl_suffix}@{pad.index}')

        # Now write the updated toml
        toml_file.write_text(toml.dumps(config))

        # Run command
        commandArray: list[str | Path] = ["/usr/bin/ymir", "-p", configPath, rom]

        return Command.Command(array=commandArray)

    def getInGameRatio(self, config, gameResolution, rom):
        if config.get_float("ymir_aspect") == 1.3333333333333333:
            return 4 / 3
        return 16 / 9
