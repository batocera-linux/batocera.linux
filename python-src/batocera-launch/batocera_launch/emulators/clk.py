from __future__ import annotations

import hashlib
import logging
import shutil
import xml.etree.ElementTree as ET
import zipfile
import zlib
from pathlib import Path
from typing import Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS
from batocera_launch import BatoceraException, Command, Emulator, HotkeysContext
from batocera_launch.paths import SYSTEM_ES_DIR, USER_ES_DIR

_logger = logging.getLogger(__name__)

# CLK looks for its ROMs as <rompath>/<machine>/<name>; Batocera names the same dumps differently.
_BIOS_ALIASES: Final = {
    'AtariST/tos100.img': ('tos100uk.img', 'c87a52c277f7952b41c639fc7bf0a43b'),
}

# ...and some it wants as a single image that Batocera only has as the separate chips of the MAME set. The chips are
# interleaved byte by byte, in this order, to make the image.
_BIOS_FROM_CHIPS: Final = {
    'Archimedes/ROM311': (
        'aa310.zip',
        ('0296,041-02.rom', '0296,042-02.rom', '0296,043-02.rom', '0296,044-02.rom'),
        0x54C0C963,
    ),
    'Macintosh/mac512k.rom': ('mac512k.zip', ('342-0220-b.u6d', '342-0221-b.u8d'), 0xCF759E0D),
}

# ...and the Electron's two ROMs, which the MAME set only has joined in one image: BASIC II, then the operating system.
_BIOS_FROM_IMAGE: Final = {
    'electron.zip': (
        'os_basic.ic2',
        {'Acorn/basic.rom': (0, 0x79434781), 'Electron/os.rom': (0x4000, 0x406A42CE)},
    ),
}
_BIOS_IMAGE_PART_SIZE: Final = 0x4000

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


def _link_bios_aliases() -> None:
    for clk_name, (batocera_name, md5) in _BIOS_ALIASES.items():
        target = BIOS / clk_name
        source = BIOS / batocera_name

        if target.exists() or not source.is_file() or hashlib.md5(source.read_bytes()).hexdigest() != md5:
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(Path('..') / batocera_name)
        _logger.debug('Linked %s to %s', target, source)


def _build_bios_from_chips() -> None:
    for clk_name, (zip_name, chips, crc32) in _BIOS_FROM_CHIPS.items():
        target = BIOS / clk_name
        source = BIOS / zip_name

        if target.exists() or not source.is_file():
            continue

        try:
            with zipfile.ZipFile(source) as archive:
                data = [archive.read(chip) for chip in chips]
        except KeyError, zipfile.BadZipFile, OSError:
            continue

        image = bytearray(sum(len(chip) for chip in data))
        for index, chip in enumerate(data):
            image[index :: len(data)] = chip

        if zlib.crc32(image) != crc32:
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(image)
        _logger.debug('Built %s from %s', target, source)


def _build_bios_from_image() -> None:
    for zip_name, (member, parts) in _BIOS_FROM_IMAGE.items():
        source = BIOS / zip_name

        if not source.is_file() or all((BIOS / name).exists() for name in parts):
            continue

        try:
            with zipfile.ZipFile(source) as archive:
                image = archive.read(member)
        except KeyError, zipfile.BadZipFile, OSError:
            continue

        for name, (offset, crc32) in parts.items():
            target = BIOS / name
            part = image[offset : offset + _BIOS_IMAGE_PART_SIZE]

            if target.exists() or zlib.crc32(part) != crc32:
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(part)
            _logger.debug('Built %s from %s', target, source)


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

        _link_bios_aliases()
        _build_bios_from_chips()
        _build_bios_from_image()

        args: list[str | Path] = ['clksignal', rom, f'--rompath={BIOS}/']

        if self.system in _SVIDEO_SYSTEMS:
            args.append('--display=SVideo')
        if self.system in _RGB_SYSTEMS:
            args.append('--display=RGB')
        if self.system in _QUICKLOAD_SYSTEMS:
            args.append('--accelerate-media-loading')

        return Command(args)
