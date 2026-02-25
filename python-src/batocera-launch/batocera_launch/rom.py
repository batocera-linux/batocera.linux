from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


def _short_name_from_path(path: str | Path) -> str:
    redname = Path(path).stem.lower()
    inpar = False
    inblock = False
    ret = ''
    for c in redname:
        if not inpar and not inblock and ((c >= 'a' and c <= 'z') or (c >= '0' and c <= '9')):
            ret += c
        elif c == '(':
            inpar = True
        elif c == ')':
            inpar = False
        elif c == '[':
            inblock = True
        elif c == ']':
            inblock = False
    return ret


class Rom(Path):
    __slots__ = ('_prepared', '_source')

    _source: Path
    _prepared: Path | None

    def __new__(cls, source: Path, prepared: Path | None, /) -> Self:
        return super().__new__(cls)

    def __init__(self, source: Path, prepared: Path | None, /) -> None:
        super().__init__(source if prepared is None else prepared)
        self._source = source
        self._prepared = prepared

    @property
    def id(self) -> str:
        return self._source.stem

    @property
    def short_id(self) -> str:
        return _short_name_from_path(self._source)

    @property
    def source(self) -> Path:
        return self._source

    @property
    def prepared(self) -> Path | None:
        return self._prepared

    @classmethod
    @asynccontextmanager
    async def prepare(cls, source: Path, /, *, writable_dir: Path | None = None) -> AsyncGenerator[Self]:
        if source.suffix != '.squashfs':
            yield cls(source, None)
        else:
            from .fs.squashfs import mount_squashfs

            async with mount_squashfs(source, writable_dir=writable_dir) as prepared_path:
                yield cls(source, prepared_path)
