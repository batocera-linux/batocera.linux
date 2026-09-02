from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path, PurePath
from typing import TYPE_CHECKING, Self, overload

from .fs.overlayfs import mount_overlayfs
from .fs.squashfs import mount_squashfs

if TYPE_CHECKING:
    from _typeshed import StrPath
    from collections.abc import AsyncGenerator, Callable, Generator, Iterator, Sequence


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

    @property
    def parent(self) -> Path:
        return Path(super().parent)

    def with_segments(self, *args: StrPath) -> Path:
        return Path(*args)

    if TYPE_CHECKING:
        # Since we override with_segments() to always return a path (rather than Rom), we
        # have to make sure the type-checker knows that's what's going to happen. These
        # are all of the methods from PurePath and Path that return Self changed to
        # return Path.

        def __truediv__(self, key: StrPath) -> Path: ...
        def __rtruediv__(self, key: StrPath) -> Path: ...
        def relative_to(self, other: StrPath, *, walk_up: bool = False) -> Path: ...
        def with_name(self, name: str) -> Path: ...
        def with_stem(self, stem: str) -> Path: ...
        def with_suffix(self, suffix: str) -> Path: ...
        def joinpath(self, *other: StrPath) -> Path: ...

        @property
        def parents(self) -> Sequence[Path]: ...

        def glob(
            self,
            pattern: str,
            *,
            case_sensitive: bool | None = None,
            recurse_symlinks: bool = False,
        ) -> Iterator[Path]: ...
        def rglob(
            self,
            pattern: str,
            *,
            case_sensitive: bool | None = None,
            recurse_symlinks: bool = False,
        ) -> Iterator[Path]: ...
        def iterdir(self) -> Generator[Path]: ...
        @overload
        def move_into[P: PurePath](self, target_dir: P) -> P: ...  # pyright: ignore[reportNoOverloadImplementation, reportOverlappingOverload]
        @overload
        def move_into(self, target_dir: StrPath) -> Path: ...
        @overload
        def move[P: PurePath](self, target: P) -> P: ...  # pyright: ignore[reportNoOverloadImplementation, reportOverlappingOverload]
        @overload
        def move(self, target: StrPath) -> Path: ...
        @overload
        def copy_into[P: PurePath](  # pyright: ignore[reportNoOverloadImplementation, reportOverlappingOverload]
            self,
            target_dir: P,
            *,
            follow_symlinks: bool = True,
            preserve_metadata: bool = False,
        ) -> P: ...
        @overload
        def copy_into(
            self,
            target_dir: StrPath,
            *,
            follow_symlinks: bool = True,
            preserve_metadata: bool = False,
        ) -> Path: ...
        @overload
        def copy[P: PurePath](  # pyright: ignore[reportNoOverloadImplementation, reportOverlappingOverload]
            self,
            target: P,
            *,
            follow_symlinks: bool = True,
            preserve_metadata: bool = False,
        ) -> P: ...
        @overload
        def copy(
            self,
            target: StrPath,
            *,
            follow_symlinks: bool = True,
            preserve_metadata: bool = False,
        ) -> Path: ...
        def readlink(self) -> Path: ...
        def rename(self, target: StrPath) -> Path: ...
        def replace(self, target: StrPath) -> Path: ...
        def resolve(self, strict: bool = False) -> Path: ...
        def absolute(self) -> Path: ...
        def expanduser(self) -> Path: ...
        def walk(
            self,
            top_down: bool = True,
            on_error: Callable[[OSError], object] | None = None,
            follow_symlinks: bool = False,
        ) -> Iterator[tuple[Path, list[str], list[str]]]: ...

    @classmethod
    def cwd(cls) -> Path:
        return Path.cwd()

    @classmethod
    @asynccontextmanager
    async def prepare(cls, source: Path, /, *, writable_dir: Path | None = None) -> AsyncGenerator[Self]:
        if source.suffix == '.squashfs':
            async with mount_squashfs(source) as squashfs_mounted:
                if writable_dir is None:
                    yield cls(source, squashfs_mounted)
                else:
                    async with mount_overlayfs(squashfs_mounted, writable_dir) as overlay_mounted:
                        yield cls(source, overlay_mounted)
        else:
            yield cls(source, None)
