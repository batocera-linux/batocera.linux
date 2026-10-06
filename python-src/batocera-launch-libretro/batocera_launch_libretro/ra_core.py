from __future__ import annotations

from batocera_common.dataclasses import cached_dataclass

from .core import Core


@cached_dataclass
class RACore(Core):
    supports_retroachievements = True
