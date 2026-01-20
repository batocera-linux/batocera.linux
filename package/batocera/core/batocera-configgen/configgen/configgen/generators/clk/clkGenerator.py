from __future__ import annotations

import shutil
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, Final

from ... import Command
from ...controller import generate_sdl_game_controller_config
from ...exceptions import BatoceraException
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

# Static temp file for extraction as CLK doens't support zipped roms
_TMP_DIR: Final = Path("/tmp/clk_extracted")
_QUICKLOAD_SYSTEMS: Final = { "amstradcpc", "archimedes", "electron", "msx1", "msx2",
    "oricatmos", "zxspectrum" }
_SVIDEO_SYSTEMS: Final = { "colecovision", "mastersystem" }
_RGB_SYSTEMS: Final = { "amstradcpc", "atarist", "electron", "enterprise", "msx1", "msx2",
    "oricatmos", "zxspectrum" }


def _openzip_file(file_path: Path, /) -> Path | None:
    if not file_path.is_file():
        return None

    if _TMP_DIR.exists():
        shutil.rmtree(_TMP_DIR)  # Remove extracted zip files (can't be done upon return from configgen)

    if str(file_path).lower().endswith('.zip'):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # Choose the largest regular file in the archive
            largest_info: zipfile.ZipInfo | None = None
            for info in zip_ref.infolist():
                # Skip directories (names ending with '/')
                if info.is_dir() if hasattr(info, "is_dir") else info.filename.endswith("/"):
                    continue

                if largest_info is None or info.file_size > largest_info.file_size:
                    largest_info = info

            if largest_info is not None:
                zip_ref.extractall(_TMP_DIR)
                return _TMP_DIR / largest_info.filename

        return None # if no files, just directories

    return file_path


class ClkGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        romzip = _openzip_file(rom)

        if romzip is None:
            raise BatoceraException(f'ROM is a directory: {rom}')

        commandArray = ["clksignal", romzip,  "--rompath=/userdata/bios/"]

        if system.name in _SVIDEO_SYSTEMS:
            commandArray.extend(["--output=SVideo"])

        if system.name in _RGB_SYSTEMS:
            commandArray.extend(["--output=RGB"])

        if system.name in _QUICKLOAD_SYSTEMS:
            commandArray.extend(["--accelerate-media-loading"])

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
