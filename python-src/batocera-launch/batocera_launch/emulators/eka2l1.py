# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

from __future__ import annotations

import asyncio
import json
import logging
import re
import shutil
import subprocess
import sys
import zipfile
import zlib
from dataclasses import field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, cast

import ruamel.yaml

from batocera_common.configparser import CaseSensitiveRawConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CACHE, CONFIGS, LOGS, ROMS, SAVES
from batocera_launch import BatoceraException, Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

_logger = logging.getLogger(__name__)

_BINARY: Final = Path('/usr/eka2l1/eka2l1_qt')
# EKA2L1 uses $XDG_DATA_HOME/EKA2L1 and changes into it at startup
_HOME: Final = CONFIGS / 'EKA2L1'
_QT_SETTINGS: Final = _HOME / 'EKA2L1.conf'
# screen filters: EKA2L1's upscaling shaders
_SHADERS: Final = _BINARY.parent / 'resources' / 'upscale'
# QColor(Qt::black) as QSettings stores it
_BLACK: Final = r'@Variant(\0\0\0\x43\x1\xff\xff\0\0\0\0\0\0\0\0)'

# portable EKA2L1 folder of the Android / Windows builds (data/ and compat/), used as is when present
_PORTABLE_ROOTS: Final = (ROMS / 'ngage' / 'EKA2L1', ROMS / 'symbian' / 'EKA2L1')
_ROM_FOLDERS: Final = (ROMS / 'ngage', ROMS / 'symbian')

_NGAGE_DEVICES: Final = ('RH-29', 'NEM-4')
# N-Gage 2.0 phone used when none is chosen: the Nokia 5320 XpressMusic
_NGAGE2_DEVICES: Final = ('RM-409',)
# Symbian versions on the EKA1 kernel, the ones the pre-9.x SIS format is made for
_EKA1_PLATFORMS: Final = frozenset({'epocu6', 'epoc6', 'epoc70', 'epoc7', 'epoc80', 'epoc81a'})
# N-Gage and S60v1 phones have 4096 colours: S60v2 ones (65536) also run their games, not the reverse
_EPOC6_PLATFORMS: Final = frozenset({'epocu6', 'epoc6'})

_SISX_UID1: Final = 0x10201A7A
_SIS_UID2_EPOC6: Final = 0x10003A12
_SIS_UID2S: Final = frozenset({0x1000006D, _SIS_UID2_EPOC6})

# Symbian language codes (TLanguage) of the Batocera languages, by locale then by language;
# EKA2L1 uses the firmware's default language when the firmware does not have it
_LANGUAGES: Final = {
    'zh_TW': 29,
    'zh_HK': 30,
    'en': 1,
    'fr': 2,
    'de': 3,
    'es': 4,
    'it': 5,
    'sv': 6,
    'da': 7,
    'nb': 8,
    'nn': 8,
    'no': 8,
    'fi': 9,
    'pt': 13,
    'tr': 14,
    'is': 15,
    'ru': 16,
    'hu': 17,
    'nl': 18,
    'cs': 25,
    'sk': 26,
    'pl': 27,
    'sl': 28,
    'zh': 31,
    'ja': 32,
    'th': 33,
    'ar': 37,
    'bg': 42,
    'ca': 44,
    'hr': 45,
    'et': 49,
    'fa': 50,
    'el': 54,
    'he': 57,
    'hi': 58,
    'id': 59,
    'ko': 65,
    'lv': 67,
    'lt': 68,
    'ms': 70,
    'ro': 78,
    'sr': 79,
    'uk': 93,
    'vi': 96,
}

# texts of the N-Gage 2.0 application, one file per language (name.r01, name.r02...)
_NGAGE_APP_TEXTS: Final = (
    ('resource', 'apps', 'ngiplay0x20003b78'),
    ('resource', 'apps', 'nafruntime', 'strings'),
    ('resource', 'apps', 'nafruntime', 'aamplaynowstr'),
)
# the video it plays each time it starts
_NGAGE_APP_VIDEO: Final = ('private', '20003b78', 'n-gage_flux320.3gp')

# default pad layout, in the evmapy .keys format, turned into an EKA2L1 key profile read through SDL
_PAD_LAYOUT: Final = Path('/usr/eka2l1/batocera-pad.keys')
_KEYBIND_PROFILE: Final = 'batocera'

# EKA2L1 controller codes (drivers/input/common.h)
_PAD_BUTTONS: Final = {
    'b': 0,
    'a': 1,
    'y': 2,
    'x': 3,
    'l3': 4,
    'r3': 5,
    'select': 6,
    'start': 7,
    'hotkey': 8,
    'pageup': 9,
    'pagedown': 10,
    'up': 11,
    'right': 12,
    'down': 13,
    'left': 14,
    'joystick1right': 300,
    'joystick1left': 301,
    'joystick1down': 302,
    'joystick1up': 303,
    'joystick2right': 304,
    'joystick2left': 305,
    'joystick2down': 306,
    'joystick2up': 307,
    'l2': 308,
    'r2': 309,
}

# phone key: (EKA2L1 scan code, Qt key of the keyboard)
_PHONE_KEYS: Final = {
    'KEY_F1': (164, 0x01000030),  # left soft key
    'KEY_F2': (165, 0x01000031),  # right soft key
    'KEY_F3': (180, 0x01000032),  # green key
    'KEY_F4': (181, 0x01000033),  # red key
    'KEY_ENTER': (167, 0x01000004),  # OK
    'KEY_UP': (16, 0x01000013),
    'KEY_DOWN': (17, 0x01000015),
    'KEY_LEFT': (14, 0x01000012),
    'KEY_RIGHT': (15, 0x01000014),
    'KEY_KPASTERISK': (42, 0x2A),
    'KEY_SLASH': (127, 0x2F),  # hash
    'KEY_BACKSPACE': (1, 0x01000003),  # C
    'KEY_LEFTSHIFT': (18, 0x01000020),  # pencil
    **{f'KEY_{digit}': (0x30 + digit, 0x30 + digit) for digit in range(10)},
}

PAD_LABELS: Final = {
    'a': 'A',
    'b': 'B',
    'x': 'X',
    'y': 'Y',
    'pageup': 'L1',
    'pagedown': 'R1',
    'l2': 'L2',
    'r2': 'R2',
    'l3': 'L3',
    'r3': 'R3',
    'select': 'SELECT',
    'start': 'START',
    'up': 'D-PAD ▲',
    'down': 'D-PAD ▼',
    'left': 'D-PAD ◀',
    'right': 'D-PAD ▶',
    'joystick1up': 'L-STICK ▲',
    'joystick1down': 'L-STICK ▼',
    'joystick1left': 'L-STICK ◀',
    'joystick1right': 'L-STICK ▶',
    'joystick2up': 'R-STICK ▲',
    'joystick2down': 'R-STICK ▼',
    'joystick2left': 'R-STICK ◀',
    'joystick2right': 'R-STICK ▶',
}
# everything but the hotkey, which opens the remapping screen
REMAPPABLE: Final = frozenset(PAD_LABELS)


def _u32(data: bytes, offset: int, /) -> int:
    return int.from_bytes(data[offset : offset + 4], 'little')


def _portable_root() -> Path | None:
    return next((root for root in _PORTABLE_ROOTS if (root / 'data' / 'devices.yml').is_file()), None)


def _storage(portable_root: Path | None, /) -> Path:
    return portable_root / 'data' if portable_root is not None else SAVES / 'eka2l1'


def _devices(storage: Path, /) -> dict[str, str]:
    # firmware code -> platform
    devices_file = storage / 'devices.yml'
    if not devices_file.is_file():
        return {}

    with devices_file.open() as fp:
        devices = cast('dict[str, dict[str, Any]] | None', ruamel.yaml.YAML(typ='safe').load(fp))  # pyright: ignore

    return {str(info.get('firmcode', code)): str(info.get('platver', '')) for code, info in (devices or {}).items()}


def _find_device(devices: Iterable[str], code: str, /) -> str | None:
    return next((device for device in devices if device.lower() == code.lower()), None)


def _first_device(devices: Iterable[str], codes: Iterable[str], /) -> str | None:
    return next((found for code in codes if (found := _find_device(devices, code))), None)


def _child(folder: Path, /, *names: str) -> Path | None:
    # Symbian paths are not case sensitive
    for name in names:
        try:
            folder = next(entry for entry in folder.iterdir() if entry.name.lower() == name.lower())
        except OSError, StopIteration:
            return None
    return folder


def _drive(storage: Path, device: str, letter: str, /) -> Path:
    # a device installed with its own drives has them in drives/<device>
    own = storage / 'drives' / device.lower() / letter
    return own if own.is_dir() else storage / 'drives' / letter


def _firmware_languages(storage: Path, device: str, /) -> tuple[list[int], int | None]:
    # languages of the firmware, and its default one (resource/bootdata/languages.txt: "01,d", "03"...)
    languages_file = _child(storage / 'drives' / 'z' / device.lower(), 'resource', 'bootdata', 'languages.txt')
    if languages_file is None:
        return [], None

    try:
        data = languages_file.read_bytes()
    except OSError:
        return [], None

    if data[:2] in (b'\xff\xfe', b'\xfe\xff'):
        text = data.decode('utf-16')
    else:
        text = data.decode('utf-16-le' if b'\0' in data else 'latin-1', errors='replace')
    languages: list[int] = []
    default = None
    for code, flags in re.findall(r'^\s*(\d+)\s*(?:,\s*(\w*))?', text, re.MULTILINE):
        languages.append(int(code))
        if flags.lower() == 'd':
            default = int(code)
    return languages, default


def _localise_ngage_app(storage: Path, device: str, language: int, /) -> None:
    # Without the language in its firmware, the phone runs in its default language and the N-Gage 2.0 application
    # shows the texts of that language: its texts in the wanted one take their place, the original is kept aside.
    languages, default = _firmware_languages(storage, device)
    swap = default is not None and language not in languages

    for letter in ('c', 'e'):
        drive = _drive(storage, device, letter)
        for *folders, name in _NGAGE_APP_TEXTS:
            if default is None or (folder := _child(drive, *folders)) is None:
                continue
            if (shown := _child(folder, f'{name}.r{default:02d}')) is None:
                continue

            original = shown.with_name(f'{shown.name}.batocera')
            translated = _child(folder, f'{name}.r{language:02d}') if swap else None
            if translated is not None:
                if not original.exists():
                    shown.rename(original)
                shutil.copyfile(translated, shown)
            elif original.exists():
                original.replace(shown)


def _show_ngage_app_video(storage: Path, device: str, show: bool, /) -> None:
    # without it, the N-Gage 2.0 application starts on its menu: the video is kept aside in its folder
    *folders, name = _NGAGE_APP_VIDEO
    for letter in ('c', 'e'):
        if (folder := _child(_drive(storage, device, letter), *folders)) is None:
            continue
        video = _child(folder, name)
        aside = _child(folder, f'{name}.batocera')
        if show and video is None and aside is not None:
            aside.rename(aside.with_name(aside.name.removesuffix('.batocera')))
        elif not show and video is not None:
            video.replace(video.with_name(f'{video.name}.batocera'))


def _is_installed(storage: Path, device: str, package: int, /) -> bool:
    return any(
        (drives / 'c' / 'sys' / 'install' / 'sisregistry' / f'{package:08x}').is_dir()
        for drives in (storage / 'drives', storage / 'drives' / device.lower())
    )


def _shortcut(path: Path, /) -> tuple[int, str | None]:
    # the .json the Android build exports: {AppUid, AppName, DeviceCode}
    try:
        info = cast('dict[str, Any]', json.loads(path.read_text(encoding='utf-8')))
        uid = int(info['AppUid'], 0) if isinstance(info['AppUid'], str) else int(info['AppUid'])
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise BatoceraException(f'Not a valid EKA2L1 shortcut: {path.name}') from e

    return uid, str(info.get('DeviceCode') or '') or None


def _sis_uids(path: Path, /) -> tuple[int, int, bool]:
    # package UID, application UID, Symbian 9 package
    with path.open('rb') as fp:
        header = fp.read(12)

    if _u32(header, 0) == _SISX_UID1:
        return _u32(header, 8), _u32(header, 8), True
    if len(header) == 12 and _u32(header, 4) in _SIS_UID2S:
        package = _u32(header, 0)
        return package, _old_sis_app_uid(path.read_bytes()) or package, False

    raise BatoceraException(f'Not a SIS package: {path.name}')


def _old_sis_app_uid(data: bytes, /) -> int | None:
    # the package UID is not always the application's: read the .app it installs (EKA2L1's loader/src/sis_old.cpp)
    langs, files, position = (
        int.from_bytes(data[18:20], 'little'),
        int.from_bytes(data[20:22], 'little'),
        _u32(data, 52),
    )
    for _ in range(files):
        record = _u32(data, position)
        position += 4
        if record in (0, 1):  # a file, one per language
            count = langs if record == 1 else 1
            name_start, name_length = _u32(data, position + 20), _u32(data, position + 16)
            length, start = _u32(data, position + 24), _u32(data, position + 24 + 4 * count)
            position += 24 + 8 * count + (4 * count + 8 if _u32(data, 4) == _SIS_UID2_EPOC6 else 0)
            if data[name_start : name_start + name_length].decode('utf-16-le', 'ignore').lower().endswith('.app'):
                try:
                    header = zlib.decompressobj().decompress(data[start : start + length], 12)
                except zlib.error:
                    header = data[start : start + 12]
                return _u32(header, 8) if len(header) >= 12 else None
        elif record in (3, 4):  # if, else if
            position += 4 + _u32(data, position)
        elif record not in (5, 6):  # else, end if
            return None
    return None


def _sis_fields(data: bytes, start: int, end: int, kind: int | None = None, /) -> Iterator[tuple[int, int, int]]:
    # SIS v9 fields: type (not repeated in an array), length on 31 or 63 bits, then the data padded to 4 bytes
    pos = start
    while pos + 8 <= end:
        if kind is None:
            field_kind = _u32(data, pos)
            pos += 4
        else:
            field_kind = kind
        length = _u32(data, pos)
        pos += 4
        if length & 0x80000000:
            length = (length & 0x7FFFFFFF) | (_u32(data, pos) << 31)
            pos += 4
        if pos + length > end:
            return
        yield field_kind, pos, length
        pos += length + (-length % 4)


def _sis_children(data: bytes, start: int, length: int, /) -> Iterator[tuple[int, int, int]]:
    # fields of a field, with the elements of its arrays in their place
    for kind, pos, size in _sis_fields(data, start, start + length):
        if kind == 2:
            yield from _sis_fields(data, pos + 4, pos + size, _u32(data, pos))
        else:
            yield kind, pos, size


def _sis_uncompress(data: bytes, start: int, length: int, /) -> bytes:
    # SISCompressed: algorithm (1 = zlib), uncompressed size, data
    content = data[start + 12 : start + length]
    return zlib.decompress(content) if _u32(data, start) == 1 else content


def _sis_file(data: bytes, target: str, /) -> bytes | None:
    # a file the package installs (from its own install block, not from its embedded packages)
    contents = next(((pos, size) for kind, pos, size in _sis_fields(data, 16, len(data)) if kind == 12), None)
    if contents is None:
        return None
    parts = list(_sis_fields(data, contents[0], contents[0] + contents[1]))
    controller = next((_sis_uncompress(data, pos, size) for kind, pos, size in parts if kind == 3), b'')
    file_index = None
    blocks = [(0, len(controller))]
    while blocks and file_index is None:
        start, length = blocks.pop()
        for kind, pos, size in _sis_children(controller, start, length):
            if kind == 24:
                name_kind, name_pos, name_size = next(_sis_fields(controller, pos, pos + size))
                name = controller[name_pos : name_pos + name_size].decode('utf-16-le', 'replace')
                if name_kind == 1 and name.lower() == target.lower():
                    file_index = _u32(controller, pos + size - 4)
                    break
            elif kind in (26, 27, 28) or (kind == 13 and start == 0):  # if, else if, install block, the controller
                blocks.append((pos, size))
    if file_index is None:
        return None

    # SISData: data units, the first one holds the files of this package
    data_field = next(((pos, size) for kind, pos, size in parts if kind == 30), None)
    if data_field is None:
        return None
    unit = next(_sis_children(data, *data_field), None)
    files = list(_sis_children(data, unit[1], unit[2])) if unit else []
    if file_index >= len(files):
        return None
    _, pos, size = files[file_index]
    compressed = next(_sis_fields(data, pos, pos + size), None)
    return _sis_uncompress(data, compressed[1], compressed[2]) if compressed else None


_NGAGE_APP_UID: Final = 0x20007B39  # the N-Gage application of N-Gage 2.0


def _ngage2_game(path: Path, /) -> tuple[bytes, int, str]:
    # A .n-gage holds the retailer's details, the package the N-Gage application shows (icons, achievements)
    # and the game's own package: that package, its UID and the executable that gameinfo.xml names
    data = path.read_bytes()
    boundary = re.search(rb'boundary="?([^";\r\n]+)', data)
    game = None
    for part in data.split(b'--' + boundary.group(1)) if boundary else ():
        header_end = re.search(rb'\r?\n\r?\n', part)
        if header_end and b'<Game>' in part[: header_end.start()]:
            game = part[header_end.end() :].removesuffix(b'\n').removesuffix(b'\r')
            break
    if game is None or _u32(game, 0) != _SISX_UID1:
        raise BatoceraException(f'Not an N-Gage 2.0 game: {path.name}')
    # header, then SISContents: type, length, data
    if 24 + _u32(game, 20) > len(game):
        raise BatoceraException(f'Incomplete N-Gage 2.0 game, the file is cut: {path.name}')

    info = _sis_file(game, r'c:\private\20007b38\import\gameinfo.xml') or b''
    if (exe := re.search(rb'<GameExeFileName>\s*([^<\s]+)', info)) is None:
        raise BatoceraException(f'No game executable named in {path.name}')
    return game, _u32(game, 8), exe.group(1).decode()


def _card_uids(path: Path, /) -> list[int]:
    # applications of a game card dump: <...>/system/apps/<app>/<app>.aif
    uids: list[int] = []
    try:
        with zipfile.ZipFile(path) as card:
            for entry in card.infolist():
                parts = entry.filename.lower().split('/')
                if len(parts) >= 4 and parts[-4:-2] == ['system', 'apps'] and parts[-1].endswith('.aif'):
                    uids.append(_u32(card.read(entry), 8))
    except OSError, zipfile.BadZipFile:
        _logger.debug('Unable to read the applications of %s', path, exc_info=True)

    return uids


def _rom_uids(rom: Path, /) -> list[int]:
    try:
        match rom.suffix.lower():
            case '.json':
                return [_shortcut(rom)[0]]
            case '.sis' | '.sisx':
                return list(_sis_uids(rom)[:2])
            case '.zip':
                return _card_uids(rom)
            case _:
                return []
    except OSError, BatoceraException:
        return []


def _caption(aif: Path, /) -> str | None:
    # <app>_caption.rsc: a length, 0xAB to align, then the caption in UTF-16
    if (caption := _child(aif.parent, f'{aif.stem}_caption.rsc')) is None:
        return None

    data = caption.read_bytes()
    if len(data) < 6:
        return None
    start = 6 if data[5] == 0xAB else 5
    text = data[start : start + 2 * data[4]].decode('utf-16-le', 'ignore').strip()
    return text if text and text.isprintable() else None


def _write_shortcuts(storage: Path, /) -> bool:
    # a .json (the format of the Android build) for each installed N-Gage game that no file starts yet
    devices = _devices(storage)
    device = next((found for code in _NGAGE_DEVICES if (found := _find_device(devices, code))), None)
    if device is None:
        return False

    covered: set[int] = set()
    names: set[str] = set()
    for folder in _ROM_FOLDERS:
        for rom in folder.iterdir() if folder.is_dir() else ():
            if rom.is_file():
                covered.update(_rom_uids(rom))
                # hand-made shortcuts may carry another UID, but end with the application's name
                if rom.suffix.lower() == '.json':
                    names.add(rom.stem.rpartition(' - ')[2].upper())

    written = False
    for drive in (_drive(storage, device, 'c'), _drive(storage, device, 'e')):
        if (apps := _child(drive, 'system', 'apps')) is None:
            continue

        # System\Apps\<app>\<app>.aif, or one folder deeper for collections
        for aif in sorted([*apps.glob('*/*'), *apps.glob('*/*/*')]):
            if aif.suffix.lower() != '.aif' or not aif.is_file():
                continue

            uid, name, app = _u32(aif.read_bytes(), 8), _caption(aif) or aif.stem, aif.stem.upper()
            shortcut = _ROM_FOLDERS[0] / (re.sub(r'[/\\:*?"<>|]', '_', f'{name} - {app}') + '.json')
            if uid in covered or app in names or shortcut.exists():
                continue

            shortcut.write_text(
                json.dumps({'AppUid': uid, 'AppName': name, 'DeviceCode': device}, indent=2) + '\n', encoding='utf-8'
            )
            _logger.info('Shortcut for the installed game %s: %s', name, shortcut.name)
            covered.add(uid)
            names.add(app)
            written = True

    return written


def _list_installed_games(storage: Path, /) -> None:
    try:
        if not _write_shortcuts(storage):
            return
    except OSError:
        _logger.warning('Unable to list the installed games', exc_info=True)
        return

    # ES only answers once this launch is over: ask it from a detached shell, like batocera-storage-manager
    subprocess.Popen(
        [
            'sh',
            '-c',
            'for i in $(seq 60); do '
            'curl -s --connect-timeout 1 http://127.0.0.1:1234/isIdle | grep -q true '
            '&& exec curl -s --max-time 10 http://127.0.0.1:1234/reloadgames; '
            'sleep 1; done',
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def _sync_compat(source: Path, destination: Path, /) -> None:
    # per-game settings, copied by date: /userdata can be exFAT (no links), where dates are 2 seconds precise
    if not source.is_dir():
        return

    destination.mkdir(parents=True, exist_ok=True)
    for setting in source.iterdir():
        target = destination / setting.name
        if setting.suffix.lower() not in ('.yml', '.json') or not setting.is_file():
            continue
        if not target.is_file() or setting.stat().st_mtime > target.stat().st_mtime + 2:
            shutil.copy2(setting, target)


def _write_config(storage: Path, portable_root: Path | None, /, **values: object) -> None:
    config_file = _HOME / 'config.yml'

    yaml = ruamel.yaml.YAML()
    config: dict[str, Any] = {}
    if config_file.is_file():
        with config_file.open() as fp:
            config = cast('dict[str, Any] | None', yaml.load(fp)) or {}  # pyright: ignore

    config['data-storage'] = str(storage)
    config['stop-warn-touchscreen-disabled'] = True
    config.update({key.replace('_', '-'): value for key, value in values.items()})

    _HOME.mkdir(parents=True, exist_ok=True)
    with config_file.open('w') as fp:
        yaml.dump(config, fp)  # pyright: ignore

    # black around the screen, instead of light grey
    qt_settings = CaseSensitiveRawConfigParser(strict=False)
    if _QT_SETTINGS.is_file():
        qt_settings.read(_QT_SETTINGS)
    if not qt_settings.has_section('General'):
        qt_settings.add_section('General')
    qt_settings.set('General', 'backgroundDisplayColor', _BLACK)
    with _QT_SETTINGS.open('w') as fp:
        qt_settings.write(fp, space_around_delimiters=False)

    if portable_root is not None:
        _sync_compat(portable_root / 'compat', _HOME / 'compat')


def _pad_layout_files(rom: Path, /) -> tuple[Path, ...]:
    return (rom.parent / f'{rom.name}.pad.keys', _HOME / 'batocera-pad.keys', _PAD_LAYOUT)


def _read_pad_layout(rom: Path, /) -> list[tuple[str, str]]:
    for path in _pad_layout_files(rom):
        if not path.is_file():
            continue

        try:
            actions = cast('list[dict[str, object]]', json.loads(path.read_text())['actions_player1'])
        except OSError, ValueError, KeyError, TypeError:
            _logger.warning('Unable to read the pad layout %s', path, exc_info=True)
            continue

        return [
            (trigger, target)
            for action in actions
            if action.get('type') == 'key'
            and isinstance(trigger := action.get('trigger'), str)
            and isinstance(target := action.get('target'), str)
        ]

    return []


def _write_keybind_profile(layout: Iterable[tuple[str, str]], /) -> None:
    binds: list[dict[str, object]] = [
        {'source': {'type': 'key', 'data': {'keycode': qt_key}}, 'target': scan_code}
        for scan_code, qt_key in _PHONE_KEYS.values()
    ]

    for trigger, target in layout:
        button, phone_key = _PAD_BUTTONS.get(trigger), _PHONE_KEYS.get(target)
        if button is None or phone_key is None:
            continue
        # EKA2L1 matches pads by SDL index
        binds.extend(
            {
                'source': {'type': 'controller', 'data': {'controller_id': pad, 'button_id': button}},
                'target': phone_key[0],
            }
            for pad in range(4)
        )

    # moved into place: a running EKA2L1 watches the folder and reloads the profile
    (_HOME / 'bindings').mkdir(parents=True, exist_ok=True)
    temporary = _HOME / f'{_KEYBIND_PROFILE}.yml.tmp'
    with temporary.open('w') as fp:
        ruamel.yaml.YAML().dump(binds, fp)  # pyright: ignore
    temporary.replace(_HOME / 'bindings' / f'{_KEYBIND_PROFILE}.yml')


def remap(layout: Iterable[tuple[str, str]], trigger: str, target: str | None, /) -> list[tuple[str, str]]:
    remapped = [(pad_button, phone_key) for pad_button, phone_key in layout if pad_button != trigger]
    if target is not None:
        remapped.append((trigger, target))
    return remapped


def save_game_pad_layout(rom: Path, layout: Iterable[tuple[str, str]], /) -> None:
    actions = [{'trigger': trigger, 'type': 'key', 'target': target} for trigger, target in layout]
    game_file = _pad_layout_files(rom)[0]
    temporary = game_file.with_name(f'{game_file.name}.tmp')
    temporary.write_text(json.dumps({'actions_player1': actions}, indent=4) + '\n')
    temporary.replace(game_file)

    _write_keybind_profile(_read_pad_layout(rom))


def _app_setting_file(uid: int, /) -> Path:
    # named as EKA2L1 names them
    return _HOME / 'compat' / f'{uid:X}.yml'


def screen_filters() -> list[str]:
    return sorted((shader.stem for shader in _SHADERS.glob('*.frag')), key=str.casefold)


def game_screen_filter(uids: Iterable[int], /) -> str | None:
    for uid in uids:
        if not (setting_file := _app_setting_file(uid)).is_file():
            continue
        try:
            with setting_file.open() as fp:
                setting = cast('dict[str, Any] | None', ruamel.yaml.YAML().load(fp)) or {}  # pyright: ignore
        except OSError, ruamel.yaml.YAMLError:
            _logger.warning('Unable to read %s', setting_file, exc_info=True)
            continue
        shader = str(setting.get('filter-shader-path') or '')
        return None if shader.lower() in ('', 'default') else shader
    return None


def save_game_screen_filter(uids: Iterable[int], shader: str | None, /) -> None:
    yaml = ruamel.yaml.YAML()
    for uid in uids:
        setting_file = _app_setting_file(uid)
        setting: dict[str, Any] = {}
        if setting_file.is_file():
            with setting_file.open() as fp:
                setting = cast('dict[str, Any] | None', yaml.load(fp)) or {}  # pyright: ignore
        setting['filter-shader-path'] = shader or 'Default'
        if shader is not None:
            # the game drawn at its own size, the shader enlarging it
            setting['screen-upscale-method'] = 1

        # moved into place: a running EKA2L1 watches the folder and applies the filter of the game it shows
        setting_file.parent.mkdir(parents=True, exist_ok=True)
        temporary = _HOME / f'{setting_file.name}.tmp'
        with temporary.open('w') as fp:
            yaml.dump(setting, fp)  # pyright: ignore
        temporary.replace(setting_file)


# eka2l1-config desktop application (batocera-config-eka2l1)
def prepare_standalone() -> None:
    portable_root = _portable_root()
    storage = _storage(portable_root)
    storage.mkdir(parents=True, exist_ok=True)
    _write_config(storage, portable_root)


def finish_standalone() -> None:
    portable_root = _portable_root()
    if portable_root is not None and (portable_root / 'compat').is_dir():
        _sync_compat(_HOME / 'compat', portable_root / 'compat')
    _list_installed_games(_storage(portable_root))


@cached_dataclass
class Eka2l1(Emulator):
    needs_sdl_game_controller_config = True

    # the applications the game may run, for their per-game settings
    _app_uids: list[int] = field(init=False, default_factory=list[int])
    _remapper: asyncio.subprocess.Process | None = field(init=False, default=None)

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'eka2l1',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @cached_property
    def config_dir(self) -> Path:
        return _HOME

    @cached_property
    def saves_dir(self) -> Path:
        return self.data_storage

    @cached_property
    def portable_root(self) -> Path | None:
        return _portable_root()

    @cached_property
    def data_storage(self) -> Path:
        return _storage(self.portable_root)

    @cached_property
    def pad_layout(self) -> list[tuple[str, str]]:
        return _read_pad_layout(self.rom)

    @cached_property
    def in_game_ratio(self) -> float:
        # N-Gage and most S60 phones
        return 176 / 208

    def _skin(self, setting: str, /) -> dict[str, object]:
        # picture of the phone around the game, from the Android build's screen profiles
        values: dict[str, object] = {
            'background_image': '',
            'background_image_opacity': 255,
            'background_image_keep_aspect': False,
            'screen_scale_ratio': 100,
        }

        skin = self.config.get_str(setting, 'none')
        profile = (self.portable_root or _PORTABLE_ROOTS[0]) / 'android' / 'profiles' / skin
        if skin == 'none' or not (profile / 'background').is_file():
            return values

        settings: dict[str, Any] = {}
        try:
            settings = json.loads((profile / 'config.json').read_text())
        except OSError, ValueError:
            _logger.warning('Unable to read %s', profile / 'config.json')

        values['background_image'] = str(profile / 'background')
        values['background_image_opacity'] = round(int(settings.get('ScreenBackgroundImageOpacity', 100)) * 255 / 100)
        values['background_image_keep_aspect'] = True
        values['screen_scale_ratio'] = int(settings.get('ScreenScaleRatio', 100))
        return values

    def _launch_args(self, devices: dict[str, str]) -> tuple[list[str | Path], list[int]]:
        # arguments, and the applications the game may run (for their per-game settings)
        match self.rom.suffix.lower():
            case '.json':
                uid, code = _shortcut(self.rom)
                if code is None:
                    raise BatoceraException(f'No DeviceCode in {self.rom.name}')
                if (device := _find_device(devices, code)) is None:
                    raise BatoceraException(f'Device {code} is not installed in EKA2L1')
                if self.system == 'ngage' and devices[device] not in _EKA1_PLATFORMS:
                    # N-Gage 2.0: the phone chosen for it, when installed
                    device = _first_device(devices, self._models('eka2l1_ngage2_device', _NGAGE2_DEVICES)) or device
                return ['--device', device, '--run', f'0x{uid:08X}'], [uid]

            case '.sis' | '.sisx':
                package, uid, is_sisx = _sis_uids(self.rom)
                candidates = [code for code, platform in devices.items() if (platform in _EKA1_PLATFORMS) != is_sisx]
                device = min(candidates, key=lambda code: devices[code] in _EPOC6_PLATFORMS, default=None)
                if device is None:
                    raise BatoceraException(
                        f'No {"Symbian 9 (S60v3)" if is_sisx else "Symbian 6-8 (S60v1/v2, N-Gage)"} device installed in EKA2L1'
                    )

                args: list[str | Path] = ['--device', device]
                if not _is_installed(self.data_storage, device, package):
                    args += ['--install', self.rom]
                return [*args, '--run', f'0x{uid:08X}'], [uid]

            case '.n-gage':
                # N-Gage 2.0 game: installed by the N-Gage application the first time, then started without it
                candidates = [code for code, platform in devices.items() if platform not in _EKA1_PLATFORMS]
                device = _first_device(candidates, self._models('eka2l1_ngage2_device', _NGAGE2_DEVICES))
                if (device := device or next(iter(candidates), None)) is None:
                    raise BatoceraException('No Symbian 9 (S60v3) phone installed in EKA2L1 for N-Gage 2.0')

                _, uid, exe = _ngage2_game(self.rom)
                args = ['--device', device]
                letter = next(
                    (
                        letter
                        for letter in ('c', 'e')
                        if _child(_drive(self.data_storage, device, letter), 'sys', 'bin', exe)
                    ),
                    None,
                )
                if letter is None:
                    # The N-Gage application installs what it finds in E:\n-gage when it starts, and lists the game
                    # with its achievements. A game installed without it hands its package back to the application
                    # while it runs, which closes it.
                    drive_e = _drive(self.data_storage, device, 'e')
                    inbox = _child(drive_e, 'n-gage') or drive_e / 'n-gage'
                    inbox.mkdir(parents=True, exist_ok=True)
                    if _child(inbox, self.rom.name) is None:
                        try:
                            (inbox / self.rom.name).hardlink_to(self.rom)
                        except OSError:
                            shutil.copyfile(self.rom, inbox / self.rom.name)
                    return [*args, '--run', f'0x{_NGAGE_APP_UID:08X}'], [_NGAGE_APP_UID]
                return [*args, '--run', f'{letter.upper()}:\\sys\\bin\\{exe}'], [uid]

            case '.jar':
                # MIDP-1.0 MIDlets run through KMidRun, which only Symbian 6 devices have; the N-Gage screen suits most of them
                candidates = [code for code, platform in devices.items() if platform in _EPOC6_PLATFORMS]
                device = _first_device(candidates, _NGAGE_DEVICES)
                if (device := device or next(iter(candidates), None)) is None:
                    raise BatoceraException('No Symbian 6 (S60v1, N-Gage) device installed in EKA2L1')
                return ['--device', device, '--jar', self.rom], []

            case _:
                # game card dump, mounted as the memory card
                codes = self._models('eka2l1_ngage_device', _NGAGE_DEVICES)
                if (device := _first_device(devices, codes)) is None:
                    raise BatoceraException(f'No N-Gage device installed in EKA2L1 ({" or ".join(codes)})')
                return ['--device', device, '--mount', self.rom, '--runng'], _card_uids(self.rom)

    def _models(self, setting: str, default: tuple[str, ...], /) -> tuple[str, ...]:
        # the model chosen first, then the usual ones when it is not installed
        wanted = self.config.get_str(setting, 'auto')
        return default if wanted == 'auto' else (wanted, *(code for code in default if code != wanted))

    async def configure(self) -> Command:
        devices = _devices(self.data_storage)
        if not devices:
            raise BatoceraException(f'No device installed in EKA2L1 ({self.data_storage})')

        args, uids = self._launch_args(devices)
        self._app_uids = uids
        device = str(args[args.index('--device') + 1])
        ngage2 = self.system == 'ngage' and devices[device] not in _EKA1_PLATFORMS

        values: dict[str, object] = {
            'enable_nearest_neighbor_filter': self.config.get_bool('eka2l1_nearest_filter', True),
            'rtos_level': self.config.get_str('eka2l1_rtos_level', 'mid'),
            'current_keybind_profile': _KEYBIND_PROFILE,
            **self._skin('eka2l1_ngage2_skin' if ngage2 else 'eka2l1_skin'),
            # N-Gage 2.0 phones are drawn lying for landscape games: they stand up when the game turns to portrait.
            # N-Gage games are in portrait on the console held sideways.
            'background_image_follow_rotation': ngage2,
        }
        if (language := self.config.get_int('eka2l1_language')) is None:
            # the language of Batocera
            locale = self.config.get_str('system.language', 'en_US')
            language = _LANGUAGES.get(locale, _LANGUAGES.get(locale.split('_')[0], 1))
        values['language'] = language

        _write_config(self.data_storage, self.portable_root, **values)
        _write_keybind_profile(self.pad_layout)
        _localise_ngage_app(self.data_storage, device, language)
        if ngage2:
            _show_ngage_app_video(self.data_storage, device, self.config.get_bool('eka2l1_ngage2_video', True))

        # EKA2L1's own settings of the game: most games are made for 30 fps or less, EKA2L1 runs them at 60 by
        # default; a game drawing its picture sideways on the phone's screen needs it turned
        app_settings: dict[str, object] = {
            key: value
            for key, value in (
                ('fps', self.config.get_int('eka2l1_fps')),
                ('screen-rotation', self.config.get_int('eka2l1_rotation')),
            )
            if value is not None
        }
        # the filter of the game, none by default (the in-game menu only tries them live)
        shader = self.config.get_str('eka2l1_shader', 'none')
        app_settings['filter-shader-path'] = 'Default' if shader == 'none' else shader
        if shader != 'none':
            # the game drawn at its own size, the shader enlarging it
            app_settings['screen-upscale-method'] = 1
        if app_settings:
            yaml = ruamel.yaml.YAML()
            (_HOME / 'compat').mkdir(parents=True, exist_ok=True)
            for uid in uids:
                setting_file = _app_setting_file(uid)
                setting: dict[str, Any] = {}
                if setting_file.is_file():
                    with setting_file.open() as fp:
                        setting = cast('dict[str, Any] | None', yaml.load(fp)) or {}  # pyright: ignore
                if any(setting.get(key) != value for key, value in app_settings.items()):
                    setting.update(app_settings)
                    with setting_file.open('w') as fp:
                        yaml.dump(setting, fp)  # pyright: ignore

        # once the game's applications are known, for its screen filter
        self._remapper = await self._start_pad_remapper()

        return Command(
            [_BINARY, *args, '--fullscreen'],
            env={
                'XDG_CONFIG_HOME': CONFIGS,
                'XDG_DATA_HOME': CONFIGS,
                'XDG_CACHE_HOME': CACHE,
                'SDL_JOYSTICK_HIDAPI': '0',
            },
        )

    async def _start_pad_remapper(self) -> asyncio.subprocess.Process | None:
        # hotkey held for 3 seconds: remap the pad of player 1 or change the screen filter in game (eka2l1_remap.py)
        if not self.config.get_bool('eka2l1_pad_remap', True):
            return None

        pad = next((c for c in self.controllers if c.player_number == 1), None)
        if pad is None or pad.type != 'joystick':
            return None

        session = Path('/var/run/eka2l1-remap.json')
        session.write_text(
            json.dumps(
                {
                    'device': pad.device_path,
                    'inputs': [[i.name, i.type, i.id, i.value, i.code] for i in pad.inputs.values()],
                    'rom': str(self.rom),
                    'layout': self.pad_layout,
                    'uids': self._app_uids,
                    'screen_height': self.resolution.height,
                }
            )
        )

        try:
            with (LOGS / 'eka2l1-remap.log').open('w') as log:
                return await asyncio.create_subprocess_exec(
                    sys.executable, '-m', 'batocera_launch.emulators.eka2l1_remap', session, stdout=log, stderr=log
                )
        except OSError:
            _logger.exception('Unable to start the pad remapping screen')
            return None

    async def run(self) -> int:
        try:
            return await super().run()
        finally:
            if (remapper := self._remapper) is not None and remapper.returncode is None:
                _logger.debug('Stopping the pad remapping screen')
                remapper.terminate()
                try:
                    await asyncio.wait_for(remapper.wait(), timeout=2)
                except TimeoutError:
                    remapper.kill()
            if self.portable_root is not None and (self.portable_root / 'compat').is_dir():
                _sync_compat(_HOME / 'compat', self.portable_root / 'compat')
            _logger.debug('Listing the installed games')
            _list_installed_games(self.data_storage)
