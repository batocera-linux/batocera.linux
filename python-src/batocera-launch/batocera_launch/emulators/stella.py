from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class Stella(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'stella',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    async def configure(self) -> Command:
        args: list[str | Path] = ['stella', self.rom]
        return Command(args)
