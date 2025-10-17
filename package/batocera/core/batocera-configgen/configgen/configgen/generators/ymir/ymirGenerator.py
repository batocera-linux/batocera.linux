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
from ...batoceraPaths import CONFIGS, SCREENSHOTS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config, write_sdl_controller_db
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

_logger = logging.getLogger(__name__)


# Mappings based on stock Ymir.toml
PERIPHERAL_BINDS = {
    "AnalogPad": {
        "sdl_map": {
            "A": ["GamepadX"], "B": ["GamepadA"], "C": ["GamepadB"],
            "X": ["GamepadLeftBumper"], "Y": ["GamepadY"], "Z": ["GamepadRightBumper"],
            "Start": ["GamepadStart"], "SwitchMode": ["GamepadLeftThumb"],
            "DPad": ["GamepadDPad"], "AnalogStick": ["GamepadLeftStick"],
            "AnalogL": ["GamepadLeftTrigger"], "AnalogR": ["GamepadRightTrigger"]
        },
        "keyboard_map": {
            1: {
                "A": ["J"], "B": ["K"], "C": ["L"], "X": ["U"], "Y": ["I"], "Z": ["O"],
                "L": ["Q"], "R": ["E"], "Up": ["W"], "Down": ["S"], "Left": ["A"], "Right": ["D"],
                "Start": ["F", "G", "H"], "SwitchMode": ["Ctrl+B"]
            },
            2: {
                "A": ["KeyPad1"], "B": ["KeyPad2"], "C": ["KeyPad3"], "X": ["KeyPad4"],
                "Y": ["KeyPad5"], "Z": ["KeyPad6"], "L": ["Insert", "KeyPad7"],
                "R": ["PageUp", "KeyPad9"], "Up": ["Home", "Up"], "Down": ["End", "Down"],
                "Left": ["Delete", "Left"], "Right": ["PageDown", "Right"],
                "Start": ["KeyPadEnter"], "SwitchMode": ["KeyPadAdd"]
            }
        }
    },
    "ControlPad": {
        "sdl_map": {
            "A": ["GamepadX"], "B": ["GamepadA"], "C": ["GamepadB"],
            "X": ["GamepadLeftBumper"], "Y": ["GamepadY"], "Z": ["GamepadRightBumper"],
            "L": ["GamepadLeftTriggerButton"], "R": ["GamepadRightTriggerButton"],
            "Start": ["GamepadStart"], "DPad": ["GamepadDPad", "GamepadLeftStick"]
        },
        "keyboard_map": {
            1: {
                "A": ["J"], "B": ["K"], "C": ["L"], "X": ["U"], "Y": ["I"], "Z": ["O"],
                "L": ["Q"], "R": ["E"], "Up": ["W"], "Down": ["S"], "Left": ["A"], "Right": ["D"],
                "Start": ["F", "G", "H"]
            },
            2: {
                "A": ["KeyPad1"], "B": ["KeyPad2"], "C": ["KeyPad3"], "X": ["KeyPad4"],
                "Y": ["KeyPad5"], "Z": ["KeyPad6"], "L": ["Insert", "KeyPad7"],
                "R": ["PageUp", "KeyPad9"], "Up": ["Home", "Up"], "Down": ["End", "Down"],
                "Left": ["Delete", "Left"], "Right": ["PageDown", "Right"], "Start": ["KeyPadEnter"]
            }
        }
    },
    "ArcadeRacer": {
        "sdl_map": {
            "A": ["GamepadX"], "B": ["GamepadA"], "C": ["GamepadB"],
            "X": ["GamepadLeftBumper"], "Y": ["GamepadY"], "Z": ["GamepadRightBumper"],
            "Start": ["GamepadStart"], "Up": ["GamepadDpadDown", "GamepadRightTriggerButton"],
            "Down": ["GamepadDpadUp", "GamepadLeftTriggerButton"], "Wheel": ["GamepadLeftStickX"]
        },
        "keyboard_map": {
            1: {
                "A": ["J"], "B": ["K"], "C": ["L"], "X": ["U"], "Y": ["I"], "Z": ["O"],
                "Start": ["F", "G", "H"], "Up": ["S"], "Down": ["W"], "WheelLeft": ["A"], "WheelRight": ["D"]
            },
            2: {
                "A": ["KeyPad1"], "B": ["KeyPad2"], "C": ["KeyPad3"], "X": ["KeyPad4"],
                "Y": ["KeyPad5"], "Z": ["KeyPad6"], "Start": ["KeyPadEnter"], "Up": ["Down", "End"],
                "Down": ["Up", "Home"], "WheelLeft": ["Delete", "Left"], "WheelRight": ["PageDown", "Right"]
            }
        }
    },
    "MissionStick": {
        "sdl_map": {
            "A": ["GamepadX"], "B": ["GamepadA"], "C": ["GamepadB"],
            "X": ["GamepadLeftBumper"], "Y": ["GamepadY"], "Z": ["GamepadRightBumper"],
            "L": ["GamepadLeftThumb"], "R": ["GamepadRightThumb"], "Start": ["GamepadStart"],
            "SwitchMode": ["GamepadBack"], "MainStick": ["GamepadLeftStick", "GamepadDPad"],
            "MainThrottle": ["GamepadLeftTrigger"], "SubStick": ["GamepadRightStick"],
            "SubThrottle": ["GamepadRightTrigger"]
        },
        "keyboard_map": {
            1: {
                "A": ["X"], "B": ["C"], "C": ["V"], "X": ["B"], "Y": ["N"], "Z": ["M"], "L": ["Q"],
                "R": ["E"], "Start": ["G"], "SwitchMode": ["Ctrl+B"], "MainUp": ["W"], "MainDown": ["S"],
                "MainLeft": ["A"], "MainRight": ["D"], "MainThrottleUp": ["R"], "MainThrottleDown": ["F"],
                "MainThrottleMax": ["Shift+R"], "MainThrottleMin": ["Shift+F"], "SubUp": ["I"], "SubDown": ["K"],
                "SubLeft": ["J"], "SubRight": ["L"], "SubThrottleUp": ["Y"], "SubThrottleDown": ["H"],
                "SubThrottleMax": ["Shift+Y"], "SubThrottleMin": ["Shift+H"]
            },
            2: {} # Player 2 keyboard for Mission Stick has no defaults in stock file
        }
    }
}

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
        backupPath = savesPath / "backup"
        exportedPath = backupPath / "exported"
        dumpsPath = savesPath / "dumps"
        screenshotPath = SCREENSHOTS / "ymir"
        romDir = Path("/userdata/roms/saturn")
        iplDir = Path("/userdata/bios")

        # Create all necessary directories
        for path in [configPath, savesPath, backupPath, exportedPath, dumpsPath, screenshotPath]:
            mkdir_if_not_exists(path)

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
                "System": {"AutoDetectRegion": True},
                "Video": {
                    "AutoResizeWindow": False, "Deinterlace": False,
                    "FullScreen": True, "ForceAspectRatio": True
                }
            }

        # --- Apply Batocera Specific Overrides ---

        # General
        general_config = config.setdefault("General", {})
        general_config.update({
            "CheckForUpdates": False,
            "IncludeNightlyBuilds": False
        })
        
        # adds [General.PathOverrides]
        path_overrides = cast("dict[str, str]", general_config.setdefault("PathOverrides", {}))
        path_overrides.update({
            "BackupMemory": str(backupPath), "CDBlockROMImages": str(romDir / "cdb/"),
            "Dumps": str(dumpsPath), "ExportedBackups": str(exportedPath),
            "IPLROMImages": str(iplDir), "PersistentState": str(configPath / "state/"),
            "ROMCartImages": str(romDir), "SaveStates": str(savesPath),
            "Screenshots": str(screenshotPath)
        })

        # Video
        video_config = config.setdefault("Video", {})
        video_config.update({
            "AutoResizeWindow": False, "DisplayVideoOutputInWindow": False, "FullScreen": True,
            "ThreadedDeinterlacer": True, "ForceAspectRatio": True, "ForceIntegerScaling": False
        })

        # Options
        video_config.update({
            "ForcedAspect": system.config.get_float("ymir_aspect", 1.5),
            "Deinterlace": system.config.get_bool("ymir_interlace", True),
            "TransparentMeshes": system.config.get_bool("ymir_meshes", False),
            "Rotation": system.config.get_str("ymir_rotation", "Normal")
        })

        # Controllers
        input_config = config.setdefault("Input", {})
        input_config.update({
            "GamepadAnalogToDigitalSensitivity": 0.20000000298023224,
            "GamepadLSDeadzone": 0.15000000596046448,
            "GamepadRSDeadzone": 0.15000000596046448
        })

        # Clear existing port configurations for the 2 supported ports
        for i in range(1, 3):
            if f"Port{i}" in input_config:
                del input_config[f"Port{i}"]

        # Configure up to a maximum of two controllers
        for pad in playersControllers[:2]:
            port_key = f"Port{pad.player_number}"
            port_config = cast("dict[str, object]", input_config.setdefault(port_key, {}))
            
            port_config["PeripheralType"] = 'AnalogPad'
            port_config["DevicePath"] = pad.device_path

            # Generate config sections for all known peripheral types for consistency
            for peripheral_name, bind_data in PERIPHERAL_BINDS.items():
                peripheral_config = cast("dict[str, object]", port_config.setdefault(peripheral_name, {}))
                binds_config = cast("dict[str, list[str]]", peripheral_config.setdefault("Binds", {}))
                
                # Start with a clean slate, then apply keyboard defaults
                binds_config.clear()
                player_keyboard_map = bind_data["keyboard_map"].get(pad.player_number, {})
                binds_config.update({key: val.copy() for key, val in player_keyboard_map.items()})

                # Append the SDL gamepad maps to the keyboard maps
                for ymir_key, sdl_suffixes in bind_data["sdl_map"].items():
                    bind_list = binds_config.setdefault(ymir_key, [])
                    for sdl_suffix in sdl_suffixes:
                        bind_list.append(f'{sdl_suffix}@{pad.index}')
        
        # Now write the updated toml
        toml_file.write_text(toml.dumps(config))

        # Write our own gamecontrollerdb.txt file before launching the game
        dbfile = configPath / "gamecontrollerdb.txt"
        write_sdl_controller_db(playersControllers, dbfile)

        # Run command
        commandArray: list[str | Path] = ["/usr/bin/ymir", "-p", configPath, rom]

        return Command.Command(array=commandArray)

    def getInGameRatio(self, config, gameResolution, rom):
        if config.get_float("ymir_aspect") == 1.3333333333333333:
            return 4 / 3
        return 16 / 9
