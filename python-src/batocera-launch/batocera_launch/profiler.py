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

from contextlib import AbstractContextManager, contextmanager
from cProfile import Profile
from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from _typeshed import StrPath
    from collections.abc import Generator
    from types import TracebackType


@dataclass(slots=True)
class Profiler(AbstractContextManager['Profiler']):
    sentinel: InitVar[StrPath]

    _sentinel_path: Path = field(init=False)
    _profile: Profile | None = field(init=False, default=None)

    def __post_init__(self, sentinel: StrPath) -> None:
        self._sentinel_path = Path(sentinel)
        if self._sentinel_path.exists():
            self._profile = Profile()

    def __enter__(self) -> Self:
        if self._profile:
            self._profile.enable()
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if self._profile:
            self._profile.disable()
            self._profile.dump_stats(self._sentinel_path.with_suffix('.prof'))

    @contextmanager
    def pause(self) -> Generator[None]:
        if not self._profile:
            yield
            return

        self._profile.disable()
        try:
            yield
        finally:
            self._profile.enable()
