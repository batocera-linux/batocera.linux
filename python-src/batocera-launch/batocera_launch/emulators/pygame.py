from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class Pygame(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'pygame',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @property
    def execution_path(self) -> Path | None:
        return self.rom.parent

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    async def configure(self) -> Command:
        return Command(['pygame', self.rom])
