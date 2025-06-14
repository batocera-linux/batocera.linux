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
import os
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import toml

from ... import Command
from ...batoceraPaths import CONFIGS, configure_emulator, mkdir_if_not_exists
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

_logger = logging.getLogger(__name__)

class YmirGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "ymir",
            "keys": {"exit": ["KEY_LEFTALT", "KEY_F4"]}
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
                with toml_file.open("r") as f:
                    config = toml.load(f)
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
        path_overrides = general_config.setdefault("PathOverrides", {})
        
        # Set the path values.
        path_overrides["BackupMemory"] = ''
        path_overrides["Dumps"] = ''
        path_overrides["ExportedBackups"] = ''
        path_overrides["IPLROMImages"] = str(iplDir)
        path_overrides["PersistentState"] = ''
        path_overrides["ROMCartImages"] = str(romDir)
        path_overrides["SaveStates"] = str(savesPath)

        # Video
        config.setdefault("Video", {})["AutoResizeWindow"] = False
        config.setdefault("Video", {})["DisplayVideoOutputInWindow"] = False
        config.setdefault("Video", {})["FullScreen"] = True

        # Options
        video_config = config.setdefault("Video", {})
        if system.config.get_bool("ymir_aspect"):
            video_config["ForcedAspect"] = 1.7777777777777778
        else:
            video_config["ForcedAspect"] = 1.3333333333333333
        if system.config.get("ymir_interlace") == "0":
            video_config["Deinterlace"] = False
        else:
            video_config["Deinterlace"] = True

        # Now write the updated toml
        with toml_file.open("w") as f:
            toml.dump(config, f)

        # Run command
        commandArray: list[str | Path] = [
            "/usr/bin/ymir",
            "-p",
            configPath,
            rom
        ]

        return Command.Command(array=commandArray)

    def getInGameRatio(self, config, gameResolution, rom):
        if config.get_bool("ymir_aspect"):
            return 16 / 9
        else:
            return 4 / 3
