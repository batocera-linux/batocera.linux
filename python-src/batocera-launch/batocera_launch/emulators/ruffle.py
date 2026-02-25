from __future__ import annotations

from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property


@cached_dataclass
class Ruffle(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'ruffle',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @property
    def needs_mouse(self) -> bool:
        return True

    async def configure(self) -> Command:
        return Command(['ruffle', self.rom])
