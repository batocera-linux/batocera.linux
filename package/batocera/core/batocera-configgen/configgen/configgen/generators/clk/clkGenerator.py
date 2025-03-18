from __future__ import annotations

from typing import TYPE_CHECKING
import os
import zipfile
import shutil
from pathlib import Path

from ... import Command
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

# Static temp file for extraction as CLK doens't support zipped roms
TMP_DIR="/tmp/clk_extracted"


def openzip_file(file_path):
    if not file_path.is_file():
        return None

    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR) # Remove extracted zip files (can't be done upon return from configgen)
    
    if str(file_path).lower().endswith('.zip'):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(TMP_DIR)
            extracted_files = zip_ref.namelist()
            
            if extracted_files:
                extracted_file_path = os.path.join(TMP_DIR, extracted_files[0])  # Assume single file in zip
                return extracted_file_path

    return file_path  # Return original file if it's not a zip


class ClkGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        romzip = openzip_file(rom)
        commandArray = ["clksignal", romzip,  "--rompath=/userdata/bios/"]

        if system.name in ["oricatmos", "amstradcpc", "archimedes", "electron", "macintosh", "msx1", "msx2",
                      "c20", "cplus4", "zx81", "zxspectrum" ]:
            commandArray.extend(["--quickload"])

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers)
            })

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "clk",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }
