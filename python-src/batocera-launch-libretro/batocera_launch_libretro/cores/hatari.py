from __future__ import annotations

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core

from ._hatari_core import HatariConfigMixin


@cached_dataclass
class Hatari(HatariConfigMixin, Core):
    pass
