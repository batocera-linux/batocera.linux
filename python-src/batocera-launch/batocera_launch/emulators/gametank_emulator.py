from __future__ import annotations

from typing import TYPE_CHECKING, Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CONFIGS
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path

_PALETTES: Final = frozenset({'capture', 'contrast', 'hdmi', 'legacy'})


@cached_dataclass
class GametankEmulator(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'gametank-emulator',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_ESC',
                'reset': 'KEY_R',
                'fastforward': 'KEY_GRAVE',
                'screenshot': 'KEY_F8',
            },
        }

    @cached_property
    def in_game_ratio(self) -> float:
        return 4 / 3

    async def configure(self) -> Command:
        args: list[str | Path] = ['gametank-emulator', '--fullscreen']

        if (palette := self.config.get_str('gametank_palette', 'capture')) in _PALETTES:
            args.append(f'--palette={palette}')

        if self.config.get_str('gametank_renderer') == 'software':
            args.append('--softrender')

        if self.config.get_bool('gametank_instantblits'):
            args.append('--instantblits')

        if self.config.get_bool('gametank_paddle'):
            args.append('--paddle')

        if not self.config.get_bool('gametank_sound', True):
            args.append('--nosound')

        args.append(self.rom)

        # the emulator keeps its pad bindings under $XDG_DATA_HOME/GameTank
        return Command(args, env={'XDG_DATA_HOME': CONFIGS})
