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
