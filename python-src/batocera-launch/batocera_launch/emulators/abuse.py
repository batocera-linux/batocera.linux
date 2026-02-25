from __future__ import annotations

from typing import Final

from batocera_common.paths import ROMS
from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

_ABUSE_DATA: Final = ROMS / 'abuse' / 'abuse_data'


@cached_dataclass
class Abuse(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'abuse',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    async def configure(self) -> Command:
        return Command(['abuse', '-datadir', _ABUSE_DATA])
