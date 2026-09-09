from __future__ import annotations

import logging
from os import environ
from struct import pack, unpack
from typing import TYPE_CHECKING, BinaryIO, Final

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from batocera_launch import Resolution
    from batocera_launch.config.config import SystemConfig

_logger = logging.getLogger(__name__)


def _read_be_int16(f: BinaryIO) -> int:
    return unpack('>H', f.read(2))[0]


def _read_be_int32(f: BinaryIO) -> int:
    return unpack('>L', f.read(4))[0]


def _read_be_int64(f: BinaryIO) -> int:
    return unpack('>Q', f.read(8))[0]


def _read_string(f: BinaryIO, x: int) -> str:
    return f.read(x).decode('utf-8')


def _read_int8(f: BinaryIO) -> int:
    return unpack('B', f.read(1))[0]


def _write_int8(f: BinaryIO, x: int) -> None:
    f.write(pack('B', x))


def _read_write_entry(f: BinaryIO, setval: Mapping[str, int]) -> None:
    item_header = _read_int8(f)
    item_type = (item_header & 0xE0) >> 5
    item_name_length = (item_header & 0x1F) + 1
    item_name = _read_string(f, item_name_length)

    if item_name in setval:
        if item_type == 3:  # byte
            _write_int8(f, setval[item_name])
            item_value = setval[item_name]
        else:
            raise ValueError(f'not writable type {item_type}')
    elif item_type == 1:  # big array
        data_size = _read_be_int16(f) + 1
        f.read(data_size)
        item_value = '[Big Array]'
    elif item_type == 2:  # small array
        data_size = _read_int8(f) + 1
        f.read(data_size)
        item_value = '[Small Array]'
    elif item_type == 3:  # byte
        item_value = _read_int8(f)
    elif item_type == 4:  # short
        item_value = _read_be_int16(f)
    elif item_type == 5:  # long
        item_value = _read_be_int32(f)
    elif item_type == 6:  # long long
        item_value = _read_be_int64(f)
    elif item_type == 7:  # bool
        item_value = _read_int8(f)
    else:
        raise ValueError(f'unknown type {item_type}')

    if not setval or item_name in setval:
        _logger.debug('%12s = %s', item_name, item_value)


def read_write_file(filepath: Path, setval: Mapping[str, int]) -> None:
    with filepath.open('rb' if not setval else 'r+b') as f:
        _read_string(f, 4)  # SCv0
        num_entries = _read_be_int16(f)
        offset_size = (num_entries + 1) * 2  # offsets
        f.read(offset_size)

        for _ in range(num_entries):
            _read_write_entry(f, setval)


_WII_LANGUAGES: Final = {
    'jp_JP': 0,
    'en_US': 1,
    'de_DE': 2,
    'fr_FR': 3,
    'es_ES': 4,
    'it_IT': 5,
    'nl_NL': 6,
    'zh_CN': 7,
    'zh_TW': 8,
    'ko_KR': 9,
}


def _wii_lang_from_environment() -> int:
    return _WII_LANGUAGES.get(environ['LANG'][:5], _WII_LANGUAGES['en_US'])


def get_ratio_from_config(config: SystemConfig, game_resolution: Resolution) -> int:
    # Sets the setting available to the Wii's internal NAND. Only has two values:
    # 0: 4:3 ; 1: 16:9
    del game_resolution
    return 1 if config.get('tv_mode') == '1' else 0


def get_sensor_bar_position(config: SystemConfig) -> int:
    # Sets the setting available to the Wii's internal NAND. Only has two values:
    # 0: BOTTOM ; 1: TOP
    return 1 if config.get('sensorbar_position') == '1' else 0


def update(config: SystemConfig, filepath: Path, game_resolution: Resolution) -> None:
    wii_lang_str = config.get_str('wii_language')
    wii_lang = int(wii_lang_str) if wii_lang_str is not None else _wii_lang_from_environment()

    read_write_file(
        filepath,
        {
            'IPL.LNG': wii_lang,
            'IPL.AR': get_ratio_from_config(config, game_resolution),
            'BT.BAR': get_sensor_bar_position(config),
        },
    )
