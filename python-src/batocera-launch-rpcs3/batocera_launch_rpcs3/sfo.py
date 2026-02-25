from __future__ import annotations

import logging
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Self, overload

if TYPE_CHECKING:
    from _typeshed import StrPath

_logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class SFO:
    data: dict[str, Any]

    @overload
    def __getattr__(self, name: Literal['TITLE']) -> str | None: ...
    @overload
    def __getattr__(self, name: Literal['TITLE_ID']) -> str | None: ...
    @overload
    def __getattr__(self, name: str) -> str | int | None: ...
    def __getattr__(self, name: str) -> str | int | None:
        return self.data.get(name, None)

    @classmethod
    def from_path(cls, path: StrPath) -> Self:
        path = Path(path)

        if not path.is_file():
            raise FileNotFoundError(f'File not found: {path}')

        sfo_data = path.read_bytes()
        data: dict[str, Any] = {}

        try:
            if len(sfo_data) < 20 or sfo_data[:4] != b'\0PSF':
                _logger.debug('Invalid PARAM.SFO file: %s', path)
            else:
                key_table_start, data_table_start, entries = struct.unpack_from('<III', sfo_data, 8)
                for offset in range(20, 20 + (entries * 16), 16):
                    key_offset, data_format, data_len, _data_max_len, data_offset = struct.unpack_from(
                        '<HHIII', sfo_data, offset
                    )

                    key_start = key_table_start + key_offset
                    key_end = sfo_data.index(b'\0', key_start)
                    key = sfo_data[key_start:key_end].decode('utf-8', errors='ignore')

                    value_start = data_table_start + data_offset
                    value_end = value_start + data_len
                    value = sfo_data[value_start:value_end]

                    if data_format == 1028:  # int32
                        value = struct.unpack('<I', value)[0]
                    else:  # utf-8 string (both null and non-null terminated)
                        value = value.decode('utf-8', errors='ignore').strip('\0 \t\r\n')

                    data[key] = value
        except OSError, ValueError, struct.error:
            _logger.debug('Could not read RPCS3 PARAM.SFO')

        return cls(data)

    @classmethod
    def from_rom(cls, rom: Path) -> Self:
        for param_sfo_dir in (rom / 'dev_hdd0' / 'game' / 'SCEEXE000', rom / 'PS3_GAME', rom):
            param_sfo = param_sfo_dir / 'PARAM.SFO'

            if param_sfo.is_file():
                return cls.from_path(param_sfo)

        return cls({})
