from __future__ import annotations

import io
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final, overload

from batocera_launch.config.configparser import CaseSensitiveConfigParser

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
    __config: CaseSensitiveConfigParser = field(init=False)

    def __post_init__(self) -> None:
        self.__config = CaseSensitiveConfigParser(interpolation=None, strict=False)

    def read(self, path: StrPath, /, *, encoding: str | None = None) -> None:
        try:
            # TODO: remove me when we migrate to Python 3.13 and can use allow_unnamed_section=True
            # pretend where have a [DEFAULT] section
            file = io.StringIO()
            file.write('[DEFAULT]\n')

            with Path(path).open(encoding=encoding) as f:
                file.write(f.read())

            file.seek(0)

            self.__config.read_file(file)
        except OSError as e:
            _logger.error(str(e))

    def write(self, path: StrPath, /, *, separator: str = '', encoding: str | None = None) -> None:
        with Path(path).open('w', encoding=encoding) as fp:
            try:
                for key, value in self.__config.items('DEFAULT'):
                    fp.write(f'{key}{separator}={separator}{value!s}\n')
            except Exception:
                # PSX Mednafen writes beetle_psx_hw_cpu_freq_scale = "100%(native)"
                # Python 2.7 is EOL and ConfigParser 2.7 takes "%(" as a won't fix error
                _logger.error('Wrong value detected (after % char maybe?), ignoring.')

    def __getitem__(self, key: str) -> str:
        return self.__config.get('DEFAULT', key)

    def __setitem__(self, key: str, value: str) -> None:
        self.__config.set('DEFAULT', key, value)

    def __delitem__(self, key: str) -> None:
        self.__config.remove_option('DEFAULT', key)

    def __contains__(self, key: str) -> bool:
        return self.__config.has_option('DEFAULT', key)

    @overload
    def get(self, key: str, /) -> str | None: ...

    @overload
    def get[T](self, key: str, /, default: T) -> str | T: ...

    def get[T](self, key: str, /, default: T | None = None) -> str | T | None:
        return self.__config.get('DEFAULT', key, fallback=default)

    def section(self, section: str, /, *, keep_defaults: bool = False) -> dict[str, str]:
        return dict(self.section_items(section, keep_defaults=keep_defaults))

    def section_items(self, section: str, /, *, keep_defaults: bool = False) -> Iterator[tuple[str, str]]:
        section_re = _section_re(section)

        for key, value in self.__config.items('DEFAULT'):
            if m := section_re.match(_protect_string(key)):
                if not keep_defaults and value in ['', 'default', 'auto']:
                    continue

                yield m.group(1), value

    def remove_section(self, section: str, /) -> None:
        section = f'{section}.'

        for key in self.__config['DEFAULT']:
            if key.startswith(section):
                self.__config.remove_option('DEFAULT', key)
