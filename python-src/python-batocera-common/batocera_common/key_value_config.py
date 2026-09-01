from __future__ import annotations

import logging
import re
from configparser import UNNAMED_SECTION
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final, overload
from typing_extensions import Sentinel

from .configparser import CaseSensitiveConfigParser

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

_logger: Final = logging.getLogger(__name__)
_sub_re: Final = re.compile(r'[^A-Za-z0-9-\.]+')


def _protect_string(string: str, /) -> str:
    return _sub_re.sub('_', string)


def _section_re(section: str, /) -> re.Pattern[str]:
    return re.compile(rf'^{_protect_string(section)}\.(.+)')


_MISSING = Sentinel('_MISSING')


@dataclass(slots=True)
class KeyValueConfig:
    path: Path | None = None
    read_encoding: str | None = field(kw_only=True, default='latin1')
    separator: str = field(kw_only=True, default='')

    __config: CaseSensitiveConfigParser = field(init=False)

    def __post_init__(self) -> None:
        self.__config = CaseSensitiveConfigParser(interpolation=None, strict=False, allow_unnamed_section=True)
        self.__config.add_section(UNNAMED_SECTION)

        if self.path is not None:
            self.read()

    def read(self, path: Path | None = None, /, *, encoding: str | _MISSING | None = _MISSING) -> None:
        path = self.path if path is None else path

        if path is None:
            raise ValueError('path must be provided')

        if encoding is _MISSING:
            encoding = self.read_encoding

        try:
            self.__config.read_string(path.read_text(encoding=encoding), source=str(path))
        except OSError:
            _logger.exception('error reading %s', path)

    def write(self, path: Path | None = None, /, *, encoding: str | None = None) -> None:
        path = self.path if path is None else path

        if path is None:
            raise ValueError('path must be provided')

        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open('w', encoding=encoding) as fp:
            try:
                for key, value in self.__config.items(UNNAMED_SECTION):
                    fp.write(f'{key}{self.separator}={self.separator}{value!s}\n')
            except Exception:
                # PSX Mednafen writes beetle_psx_hw_cpu_freq_scale = "100%(native)"
                # Python 2.7 is EOL and ConfigParser 2.7 takes "%(" as a won't fix error
                _logger.exception('Wrong value detected (after % char maybe?), ignoring.')

    def __getitem__(self, key: str) -> str:
        return self.__config.get(UNNAMED_SECTION, key)

    def __setitem__(self, key: str, value: object) -> None:
        self.__config.set(UNNAMED_SECTION, key, str(value))

    def __delitem__(self, key: str) -> None:
        self.__config.remove_option(UNNAMED_SECTION, key)

    def __contains__(self, key: str) -> bool:
        return self.__config.has_option(UNNAMED_SECTION, key)

    @overload
    def get(self, key: str, /) -> str | None: ...

    @overload
    def get[T](self, key: str, /, default: T) -> str | T: ...

    def get[T](self, key: str, /, default: T | None = None) -> str | T | None:
        return self.__config.get(UNNAMED_SECTION, key, fallback=default)

    def section(self, section: str, /, *, keep_defaults: bool = False) -> dict[str, str]:
        return dict(self.section_items(section, keep_defaults=keep_defaults))

    def section_items(self, section: str, /, *, keep_defaults: bool = False) -> Iterator[tuple[str, str]]:
        section_re = _section_re(section)

        for key, value in self.__config.items(UNNAMED_SECTION):
            if m := section_re.match(_protect_string(key)):
                if not keep_defaults and value in ['', 'default', 'auto']:
                    continue

                yield m.group(1), value

    def remove_all_starting_with(self, prefix: str, /) -> None:
        for key in self.__config[UNNAMED_SECTION]:
            if key.startswith(prefix):
                self.__config.remove_option(UNNAMED_SECTION, key)

    def remove_section(self, section: str, /) -> None:
        self.remove_all_starting_with(f'{section}.')
