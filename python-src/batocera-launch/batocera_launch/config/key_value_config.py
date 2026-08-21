from __future__ import annotations

import logging
import re
from configparser import UNNAMED_SECTION
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final, overload

from batocera_common.configparser import CaseSensitiveConfigParser

if TYPE_CHECKING:
    from _typeshed import StrPath
    from collections.abc import Iterator

_logger: Final = logging.getLogger(__name__)
_sub_re: Final = re.compile(r'[^A-Za-z0-9-\.]+')


def _protect_string(string: str, /) -> str:
    return _sub_re.sub('_', string)


def _section_re(section: str, /) -> re.Pattern[str]:
    return re.compile(rf'^{_protect_string(section)}\.(.+)')


@dataclass(slots=True)
class KeyValueConfig:
    separator: str = field(default='')

    __config: CaseSensitiveConfigParser = field(init=False)

    def __post_init__(self) -> None:
        self.__config = CaseSensitiveConfigParser(interpolation=None, strict=False, allow_unnamed_section=True)

    def read(self, path: StrPath, /, *, encoding: str | None = 'latin1') -> None:
        try:
            self.__config.read_string(Path(path).read_text(encoding=encoding), source=str(path))
        except OSError as e:
            _logger.error(str(e))

    def write(self, path: StrPath, /, *, encoding: str | None = None) -> None:
        with Path(path).open('w', encoding=encoding) as fp:
            try:
                for key, value in self.__config.items(UNNAMED_SECTION):
                    fp.write(f'{key}{self.separator}={self.separator}{value!s}\n')
            except Exception:
                # PSX Mednafen writes beetle_psx_hw_cpu_freq_scale = "100%(native)"
                # Python 2.7 is EOL and ConfigParser 2.7 takes "%(" as a won't fix error
                _logger.error('Wrong value detected (after % char maybe?), ignoring.')

    def __getitem__(self, key: str) -> str:
        return self.__config.get(UNNAMED_SECTION, key)

    def __setitem__(self, key: str, value: str) -> None:
        self.__config.set(UNNAMED_SECTION, key, value)

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
