from __future__ import annotations

from pathlib import Path

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CACHE, CONFIGS, ROMS
from batocera_launch import Command, Emulator, HotkeysContext


@cached_dataclass
class Jazz2_Native(Emulator):
    needs_sdl_game_controller_config = True
    needs_sdl_controller_db = True

    @cached_property
    def sdl_controller_db_path(self) -> Path:
        return Path('/usr/share/jazz2/gamecontrollerdb.txt')

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'jazz2',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    async def configure(self) -> Command:
        return Command(
            ['jazz2'],
            env={
                'XDG_CONFIG_HOME': CONFIGS,
                'XDG_CACHE_HOME': CACHE,
                'XDG_DATA_HOME': ROMS / 'jazz2',
                'SDL_JOYSTICK_HIDAPI': '0',
            },
        )
