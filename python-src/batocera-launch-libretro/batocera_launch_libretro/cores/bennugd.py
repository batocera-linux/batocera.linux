from __future__ import annotations

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import Core


@cached_dataclass
class BennuGD(Core):
    @property
    def disables_bezel(self) -> bool:
        return True
