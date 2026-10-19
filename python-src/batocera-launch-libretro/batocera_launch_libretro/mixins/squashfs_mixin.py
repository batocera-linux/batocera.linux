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

import itertools
from typing import TYPE_CHECKING, ClassVar

from batocera_common.dataclasses import cached_dataclass, cached_property

from ..core import Core

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from pathlib import Path


@cached_dataclass
class SquashFSMixin(Core):
    squashfs_rom_globs: ClassVar[Mapping[str, Iterable[str]]]

    @cached_property
    def rom_argument(self) -> str | Path | None:
        if (
            (globs := self.squashfs_rom_globs.get(self.system)) is not None
            and 'squashfs' in str(self.rom)
            and self.rom.is_dir()
        ):
            return next(itertools.chain(*(self.rom.glob(glob) for glob in globs)))

        return self.rom
