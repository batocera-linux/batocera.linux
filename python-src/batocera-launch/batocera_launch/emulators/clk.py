from __future__ import annotations

import shutil
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS
from batocera_launch import BatoceraException, Command, Emulator, HotkeysContext
from batocera_launch.paths import SYSTEM_ES_DIR, USER_ES_DIR

# Static temp file for extraction; CLK doesn't support zipped roms.
_TMP_DIR: Final = Path('/tmp/clk_extracted')
_QUICKLOAD_SYSTEMS: Final = {
    'amstradcpc',
    'archimedes',
    'electron',
    'msx1',
    'msx2',
    'oricatmos',
    'zxspectrum',
}
_SVIDEO_SYSTEMS: Final = {'colecovision', 'mastersystem'}
_RGB_SYSTEMS: Final = {
    'amstradcpc',
    'atarist',
    'electron',
    'enterprise',
    'msx1',
    'msx2',
    'oricatmos',
    'zxspectrum',
}
_ES_SYSTEMS_DIRS: Final = (SYSTEM_ES_DIR, USER_ES_DIR)

# Archive containers are never the loadable file we extract from a zip.
_ARCHIVE_EXTENSIONS: Final = {'zip', '7z'}


def _supported_extensions(system_name: str, /) -> set[str]:
    """Loadable file extensions for a system from es_systems*.cfg (user overrides last)."""
    extensions: set[str] = set()
    for es_dir in _ES_SYSTEMS_DIRS:
        for config in sorted(es_dir.glob('es_systems*.cfg')):
            try:
                root = ET.parse(config).getroot()
            except ET.ParseError, OSError:
                continue
            for system in root.iter('system'):
                if system.findtext('name') != system_name:
                    continue
                found = {
                    ext.lstrip('.').lower() for ext in (system.findtext('extension') or '').split()
                } - _ARCHIVE_EXTENSIONS
                if found:
                    extensions = found  # later configs override earlier ones
    return extensions


def _openzip_file(file_path: Path, valid_extensions: set[str] | None = None, /) -> Path | None:
    if not file_path.is_file():
        return None

    if _TMP_DIR.exists():
        shutil.rmtree(_TMP_DIR)  # Remove extracted zip files (can't be done upon return from configgen)

    if file_path.suffix.lower() != '.zip':
        return file_path

    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        # Prefer the largest file with a loadable extension, so CLK can identify
        # the target machine. Fall back to the largest file overall.
        best_valid: zipfile.ZipInfo | None = None
        largest_info: zipfile.ZipInfo | None = None
        for info in zip_ref.infolist():
            # Skip directories
            if info.is_dir():
                continue

            if largest_info is None or info.file_size > largest_info.file_size:
                largest_info = info

            if (
                valid_extensions
                and Path(info.filename).suffix.lower().lstrip('.') in valid_extensions
                and (best_valid is None or info.file_size > best_valid.file_size)
            ):
                best_valid = info

        chosen = best_valid or largest_info
        if chosen is None:
            return None

        zip_ref.extractall(_TMP_DIR)
        return _TMP_DIR / chosen.filename


@cached_dataclass
class Clk(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'clk',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    async def configure(self) -> Command:
        rom = _openzip_file(self.rom, _supported_extensions(self.system))

        if rom is None:
            raise BatoceraException(f'ROM is a directory: {self.rom}')

        args: list[str | Path] = ['clksignal', rom, f'--rompath={BIOS}/']

        if self.system in _SVIDEO_SYSTEMS:
            args.append('--output=SVideo')
        if self.system in _RGB_SYSTEMS:
            args.append('--output=RGB')
        if self.system in _QUICKLOAD_SYSTEMS:
            args.append('--accelerate-media-loading')

        return Command(args)
