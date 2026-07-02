from __future__ import annotations

import shutil
import xml.etree.ElementTree as ElementTree
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

_ES_SYSTEMS_DIRS: Final = (
    Path("/usr/share/emulationstation"),
    Path("/userdata/system/configs/emulationstation"),
)

# Archive containers are never the loadable file we extract from a zip.
_ARCHIVE_EXTENSIONS: Final = { "zip", "7z" }


def _supported_extensions(system_name: str, /) -> set[str]:
    """Loadable file extensions for a system, read from es_systems.cfg (honouring user
    overrides). Empty if no config can be read, in which case no filtering is applied."""
    extensions: set[str] = set()
    for es_dir in _ES_SYSTEMS_DIRS:
        for config in sorted(es_dir.glob("es_systems*.cfg")):
            try:
                root = ElementTree.parse(config).getroot()
            except (ElementTree.ParseError, OSError):
                continue
            for system in root.iter("system"):
                if system.findtext("name") != system_name:
                    continue
                found = {
                    ext.lstrip(".").lower()
                    for ext in (system.findtext("extension") or "").split()
                } - _ARCHIVE_EXTENSIONS
                if found:
                    extensions = found  # later configs override earlier ones
    return extensions


def _openzip_file(file_path: Path, valid_extensions: set[str] | None = None, /) -> Path | None:
    if not file_path.is_file():
        return None

    if _TMP_DIR.exists():
        shutil.rmtree(_TMP_DIR)  # Remove extracted zip files (can't be done upon return from configgen)

    if str(file_path).lower().endswith('.zip'):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # Prefer the largest file with a loadable extension, so CLK can identify
            # the target machine. Fall back to the largest file overall.
            best_valid: zipfile.ZipInfo | None = None
            largest_info: zipfile.ZipInfo | None = None
            for info in zip_ref.infolist():
                # Skip directories (names ending with '/')
                if info.is_dir() if hasattr(info, "is_dir") else info.filename.endswith("/"):
                    continue

                if largest_info is None or info.file_size > largest_info.file_size:
                    largest_info = info

                if valid_extensions and Path(info.filename).suffix.lower().lstrip('.') in valid_extensions:
                    if best_valid is None or info.file_size > best_valid.file_size:
                        best_valid = info

            chosen = best_valid or largest_info
            if chosen is not None:
                zip_ref.extractall(_TMP_DIR)
                return _TMP_DIR / chosen.filename

        return None # if no files, just directories

    return file_path


class ClkGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        romzip = _openzip_file(rom, _supported_extensions(system.name))

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
