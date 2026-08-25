from __future__ import annotations

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import Command, Emulator, HotkeysContext


@cached_dataclass
class Lightspark(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'lightspark',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @property
    def needs_mouse(self) -> bool:
        return True

    async def configure(self) -> Command:
        return Command(['lightspark', '-fs', '-s', 'local-with-networking', self.rom])
