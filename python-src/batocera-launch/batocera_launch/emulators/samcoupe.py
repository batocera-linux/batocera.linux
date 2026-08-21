from __future__ import annotations

from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property


@cached_dataclass
class Samcoupe(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'samcoupe',
            'keys': {
                'exit': ['KEY_LEFTCTRL', 'KEY_F12'],
                'menu': 'KEY_F10',
                'pause': 'KEY_F10',
            },
        }

    async def configure(self) -> Command:
        return Command(['simcoupe', '-fullscreen', '1', self.rom])
