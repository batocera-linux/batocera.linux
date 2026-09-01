from __future__ import annotations

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import Command, Emulator, HotkeysContext


@cached_dataclass
class Pyxel(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'pyxel',
            'keys': {'exit': 'KEY_ESC'},
        }

    async def configure(self) -> Command:
        cmd = 'play' if self.rom.suffix == '.pyxapp' else 'run'
        return Command(['/usr/bin/pyxel', cmd, self.rom])
