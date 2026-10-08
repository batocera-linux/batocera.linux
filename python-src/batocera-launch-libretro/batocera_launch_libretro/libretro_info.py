from __future__ import annotations

from configparser import UNNAMED_SECTION
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Final, Self, overload

from batocera_common.configparser import CaseSensitiveConfigParser

_RETROARCH_INFO_DIR: Final = Path('/usr/share/libretro/info')


@dataclass(slots=True)
class LibretroInfo:
    TRUE_VALUES: ClassVar = frozenset({'true', '1'})
    FALSE_VALUES: ClassVar = frozenset({'false', '0'})

    config: CaseSensitiveConfigParser

    @staticmethod
    def file(core: str, /) -> Path:
        return _RETROARCH_INFO_DIR / f'{core}_libretro.info'

    @classmethod
    def load(cls, core: str, /) -> Self | None:
        # for each core, a file /usr/lib/<core>.info must exit, otherwise, info such as rewinding/netplay will not work
        # to do a global check : cd /usr/lib/libretro && for i in *.so; do INF=$(echo $i | sed -e s+/usr/lib/libretro+/usr/share/libretro/info+ -e s+\.so+.info+); test -e "$INF" || echo $i; done
        if not (info_file := cls.file(core)).exists():
            return None

        config = CaseSensitiveConfigParser(
            interpolation=None,
            strict=False,
            delimiters=('=',),
            comment_prefixes=('#',),
            allow_unnamed_section=True,
        )
        config.add_section(UNNAMED_SECTION)

        try:
            config.read_string(info_file.read_text(), source=str(info_file))
        except OSError:
            return None

        return cls(config)

    @overload
    def get(self, key: str, /) -> str | None: ...

    @overload
    def get[T](self, key: str, /, default: T) -> str | T: ...

    def get[T](self, key: str, /, default: T | None = None) -> str | T | None:
        value = self.config.get(UNNAMED_SECTION, key, fallback=None)
        if value is None:
            return default

        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]

        return value

    def get_bool(self, key: str, /) -> bool | None:
        value = self.get(key)

        if value in self.TRUE_VALUES:
            return True

        if value in self.FALSE_VALUES:
            return False

        return None
