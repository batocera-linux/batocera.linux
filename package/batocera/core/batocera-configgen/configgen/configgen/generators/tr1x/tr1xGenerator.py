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
import shutil
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING

import requests

from ... import Command
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ...types import HotkeysContext

class TR1XGenerator(Generator):

    MUSIC_ZIP_URL = "https://lostartefacts.dev/aux/tr1x/music.zip"

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "tr1x",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "save_state": "KEY_F5", "restore_state": "KEY_F6" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        tr1xRomPath = Path(rom).parent
        tr1xSourcePath = Path("/usr/bin/tr1x")
        musicZipPath = tr1xRomPath / "music.zip"
        musicDir = tr1xRomPath / "music"

        # Ensure the destination directory exists
        tr1xRomPath.mkdir(parents=True, exist_ok=True)

        # Copy files & folders if they don’t exist
        for item in tr1xSourcePath.iterdir():
            dest = tr1xRomPath / item.name
            try:
                if item.is_dir():
                    if not dest.exists():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
            except PermissionError as e:
                _logger.debug("Permission error while copying %s -> %s: %s", item, dest, e)
            except Exception as e:
                _logger.debug("Error copying %s -> %s: %s", item, dest, e)

        # Download and extract music.zip if the music directory does not exist
        if not musicDir.exists():
            try:
                _logger.debug("Downloading music.zip from %s...", self.MUSIC_ZIP_URL)
                response = requests.get(self.MUSIC_ZIP_URL, stream=True)
                response.raise_for_status()

                # Write to music.zip
                with musicZipPath.open("wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                # Extract the zip file
                with zipfile.ZipFile(musicZipPath, "r") as zip_ref:
                    zip_ref.extractall(tr1xRomPath)

                # Remove the zip file after extraction
                musicZipPath.unlink()
                _logger.debug("Music files downloaded and extracted successfully.")
            except requests.RequestException as e:
                _logger.debug("Failed to download music.zip: %s", e)
            except zipfile.BadZipFile as e:
                _logger.debug("Error extracting music.zip: %s", e)
            except Exception as e:
                _logger.debug("Unexpected error: %s", e)

        commandArray = [tr1xRomPath / "TR1X"]

        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if gameResolution["width"] / float(gameResolution["height"]) > ((16.0 / 9.0) - 0.1):
            return 16/9
        return 4/3
