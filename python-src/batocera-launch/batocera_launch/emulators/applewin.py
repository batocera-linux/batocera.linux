from __future__ import annotations

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.key_value_config import KeyValueConfig
from batocera_launch import Command, Emulator, HotkeysContext


@cached_dataclass
class AppleWin(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'applewin',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config_file = self.config_dir / 'config.txt'

        config = KeyValueConfig(' ')
        config.read(config_file)
        config.write(config_file)

        return Command(['applewin'])
