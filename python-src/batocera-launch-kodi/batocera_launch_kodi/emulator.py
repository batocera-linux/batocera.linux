from __future__ import annotations

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import Command, Emulator, HotkeysContext

from .config import write_kodi_config


@cached_dataclass
class Kodi(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'kodi',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @cached_property
    def in_game_ratio(self) -> float:
        return self.resolution.width / self.resolution.height

    async def configure(self) -> Command:
        write_kodi_config(self.controllers)
        return Command(['/usr/bin/batocera-kodilauncher'])
