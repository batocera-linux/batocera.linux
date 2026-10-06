from __future__ import annotations

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import Command, Emulator, HotkeysContext


@cached_dataclass
class Uqm(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'uqm',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    async def configure(self) -> Command:
        (self.saves_dir / 'teams').mkdir(parents=True, exist_ok=True)
        (self.saves_dir / 'save').mkdir(parents=True, exist_ok=True)
        (self.roms_dir / 'version').touch(exist_ok=True)

        return Command(
            [
                'urquan',
                f'--contentdir={self.roms_dir}',
                f'--configdir={self.saves_dir}',
            ]
        )
