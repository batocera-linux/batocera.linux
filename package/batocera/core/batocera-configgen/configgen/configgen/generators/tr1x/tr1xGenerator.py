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

from ... import Command
from ...batoceraPaths import mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ...utils.download import DownloadException, download
from ..Generator import Generator

_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ...types import HotkeysContext

class TR1XGenerator(Generator):

    MUSIC_ZIP_URL = "https://lostartefacts.dev/aux/tr1x/music.zip"
    EXPANSION_ZIP_URL = "https://lostartefacts.dev/aux/tr1x/trub-music.zip"

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "tr1x",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "save_state": "KEY_F5", "restore_state": "KEY_F6" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        tr1xRomPath = rom.parent
        tr1xSourcePath = Path("/usr/bin/tr1x")
        musicDir = tr1xRomPath / "music"
        dataDir = tr1xRomPath / "data"

        # Ensure the destination directories exist
        mkdir_if_not_exists(tr1xRomPath)
        mkdir_if_not_exists(dataDir)

        # Copy files & folders if they don't exist
        for item in tr1xSourcePath.iterdir():
            dest = tr1xRomPath / item.name
            try:
                if item.is_dir():
                    if not dest.exists():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                    else:
                        for sub_item in item.rglob('*'):
                            sub_dest = dest / sub_item.relative_to(item)
                            if sub_item.is_dir():
                                sub_dest.mkdir(parents=True, exist_ok=True)
                            else:
                                shutil.copy2(sub_item, sub_dest)
                else:
                    shutil.copy2(item, dest)
            except PermissionError as e:
                _logger.debug("Permission error while copying %s -> %s: %s", item, dest, e)
            except Exception as e:
                _logger.debug("Error copying %s -> %s: %s", item, dest, e)

        # Download and extract music.zip if the music directory does not exist
        if not musicDir.exists():
            try:
                with (
                    download(self.MUSIC_ZIP_URL, tr1xRomPath) as downloaded,
                    zipfile.ZipFile(downloaded, "r") as zip_ref
                ):
                    # Extract the zip file
                    zip_ref.extractall(tr1xRomPath)

                _logger.debug("Music files downloaded and extracted successfully.")
            except DownloadException:
                _logger.exception("Failed to download music.zip")
            except zipfile.BadZipFile as e:
                _logger.debug("Error extracting music.zip: %s", e)
            except Exception as e:
                _logger.debug("Unexpected error: %s", e)

        # Handle the expansion pack download and extraction if enabled
        if system.config.get_bool("tr1x-expansion"):
            # Only extract if there is no file named "CAT.PHD" (case-insensitive) in the data directory
            cat_phd_exists = any(
                p for p in dataDir.rglob("*") if p.is_file() and p.name.upper() == "CAT.PHD"
            )
            if not cat_phd_exists:
                try:
                    with (
                        download(self.EXPANSION_ZIP_URL, tr1xRomPath) as downloaded,
                        zipfile.ZipFile(downloaded) as zip_ref
                    ):
                        # Extract files from the expansion zip, ignoring the top-level "DATA" directory
                        for file in zip_ref.namelist():
                            # Remove the top-level DATA/ prefix if present
                            stripped_file = file
                            if stripped_file.upper().startswith("DATA/"):
                                stripped_file = stripped_file[5:]
                            # Skip directory entries or empty names after stripping
                            if not stripped_file or file.endswith("/"):
                                continue
                            destination = dataDir / stripped_file
                            if not destination.exists():
                                destination.parent.mkdir(parents=True, exist_ok=True)
                                with zip_ref.open(file) as source, destination.open("wb") as target:
                                    shutil.copyfileobj(source, target)

                    _logger.debug("Expansion files downloaded and extracted successfully.")
                except DownloadException:
                    _logger.exception("Failed to download expansion zip")
                except zipfile.BadZipFile as e:
                    _logger.debug("Error extracting expansion zip: %s", e)
                except Exception as e:
                    _logger.debug("Unexpected error: %s", e)

            commandArray = [tr1xRomPath / "TR1X", "-gold"]
        else:
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
