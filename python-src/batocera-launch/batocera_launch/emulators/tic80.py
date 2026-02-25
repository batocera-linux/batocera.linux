from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class Tic80(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'tic80',
            'keys': {
                'exit': ['KEY_LEFTCTRL', 'KEY_Q'],
                'menu': 'KEY_ENTER',
                'reset': ['KEY_LEFTCTRL', 'KEY_R'],
            },
        }

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    async def configure(self) -> Command:
        args: list[str | Path] = ['tic80', '--fullscreen', '--skip']

        if self.rom.stem.lower() in {'surf', 'console'}:
            args.append('--cmd=surf')
        else:
            args.append(self.rom)

        return Command(args)
