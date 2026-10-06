from __future__ import annotations

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CONFIGS, ROMS
from batocera_launch import Command, Emulator, HotkeysContext


@cached_dataclass
class Taradino(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'taradino',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    async def configure(self) -> Command:
        return Command(
            ['taradino'],
            env={
                'XDG_DATA_HOME': CONFIGS,
                'XDG_DATA_DIRS': ROMS / 'rott',
                'SDL_JOYSTICK_HIDAPI': '0',
                'SDL_VIDEODRIVER': 'x11',
            },
        )
