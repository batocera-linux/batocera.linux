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

# Loadable extensions per system (mirrors es_systems.yml, minus archive containers).
# CLK picks the target machine from the file extension, so when a zip holds several
# files (e.g. a program plus a data file) we must extract a recognized one, not just
# the largest.
_LOADABLE_EXTENSIONS: Final = {
    "amstradcpc": { "dsk", "sna", "tap", "cdt", "voc" },
    "archimedes": { "mfi", "dfi", "hfe", "mfm", "td0", "imd", "d77", "d88", "1dd",
        "cqm", "cqi", "dsk", "ima", "img", "ufi", "360", "ipf", "adf", "apd", "jfd",
        "ads", "adm", "adl", "ssd", "bbc", "dsd", "st", "msa", "chd" },
    "atarist": { "st", "msa", "stx", "dim", "ipf", "hd", "gemdos" },
    "bbcmicro": { "mfi", "dfi", "hfe", "mfm", "td0", "imd", "d77", "d88", "1dd", "cqm",
        "cqi", "dsk", "ima", "img", "ufi", "360", "ipf", "ssd", "bbc", "dsd", "adf",
        "ads", "adm", "adl", "fsd", "wav", "tap", "bin" },
    "colecovision": { "bin", "col", "rom" },
    "electron": { "wav", "csw", "uef", "mfi", "dfi", "hfe", "mfm", "td0", "imd", "d77",
        "d88", "1dd", "cqm", "cqi", "dsk", "ssd", "bbc", "img", "dsd", "adf", "ads",
        "adm", "adl", "rom", "bin" },
    "enterprise": { "bas", "com", "img", "dsk", "tap", "dtf", "trn", "128", "cas",
        "cdt", "tzx" },
    "macintosh": { "dsk", "mfi", "dfi", "hfe", "mfm", "td0", "imd", "d77", "d88", "1dd",
        "cqm", "cqi", "ima", "img", "ufi", "ipf", "dc42", "woz", "2mg", "360", "chd",
        "cue", "toc", "nrg", "gdi", "iso", "cdr", "hd", "hdv", "hdi" },
    "mastersystem": { "bin", "sms" },
    "msx1": { "dsk", "mx1", "rom", "cas" },
    "msx2": { "dsk", "mx2", "rom", "cas" },
    "oricatmos": { "tap", "dsk" },
    "zxspectrum": { "tzx", "tap", "z80", "rzx", "scl", "trd", "dsk" },
}


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

                if valid_extensions and Path(info.filename).suffix.lower().lstrip('.') in valid_extensions:  # noqa: SIM102
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
        romzip = _openzip_file(rom, _LOADABLE_EXTENSIONS.get(system.name))

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
