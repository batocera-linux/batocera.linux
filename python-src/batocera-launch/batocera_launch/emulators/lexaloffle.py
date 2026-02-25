from __future__ import annotations

import os
from typing import TYPE_CHECKING, Final, NamedTuple

from batocera_common.paths import BIOS, HOME, ROMS, SCREENSHOTS

from ..command import Command
from ..dataclasses import cached_dataclass
from ..emulator import Emulator
from ..exceptions import BatoceraException
from ..functools import cached_property

if TYPE_CHECKING:
    from pathlib import Path

    from ..types import HotkeysContext


class _LexalofflePaths(NamedTuple):
    ld_lib: Path
    binary: Path
    controllers: Path
    root: Path


_SYSTEMS: Final = {
    'pico8': _LexalofflePaths(
        BIOS / 'pico-8',
        BIOS / 'pico-8' / 'pico8',
        HOME / '.lexaloffle' / 'pico-8' / 'sdl_controllers.txt',
        ROMS / 'pico8',
    ),
    'voxatron': _LexalofflePaths(
        BIOS / 'voxatron',
        BIOS / 'voxatron' / 'vox',
        HOME / '.lexaloffle' / 'Voxatron' / 'sdl_controllers.txt',
        ROMS / 'voxatron',
    ),
}


@cached_dataclass
class Lexaloffle(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'lexaloffle',
            'keys': {
                'exit': ['KEY_LEFTCTRL', 'KEY_Q'],
                'menu': 'KEY_ENTER',
                'reset': ['KEY_LEFTCTRL', 'KEY_R'],
            },
        }

    @cached_property
    def in_game_ratio(self) -> float:
        return 4 / 3

    async def configure(self) -> Command:
        if (paths := _SYSTEMS.get(self.system)) is None:
            raise BatoceraException(f'The Lexaloffle generator has been called for an unknown system: {self.system}.')

        if not paths.binary.exists():
            raise BatoceraException(f'Lexaloffle official binary not found at {paths.binary}')

        if not os.access(paths.binary, os.X_OK):
            raise BatoceraException(f'{paths.binary} is not set as executable')

        args: list[str | Path] = [
            paths.binary,
            '-desktop',
            SCREENSHOTS,
            '-windowed',
            '0',
            '-show_fps',
            '1' if self.config.show_fps else '0',
        ]

        cart = self.rom
        if cart.suffix.lower() == '.m3u':
            cart = cart.parent / cart.read_text().splitlines()[0].strip()
            args.extend(['-root_path', cart.parent])
        else:
            args.extend(['-root_path', paths.root])

        if self.rom.stem.lower() in {'splore', 'console'}:
            args.append('-splore')
        else:
            args.extend(['-run', cart])

        paths.controllers.parent.mkdir(parents=True, exist_ok=True)
        paths.controllers.write_text(self.get_sdl_game_controller_config())

        ld_library_path: str | Path = paths.ld_lib
        if existing_library_path := os.environ.get('LD_LIBRARY_PATH'):
            ld_library_path = f'{paths.ld_lib}:{existing_library_path}'

        return Command(
            args,
            env={
                'SDL_AUDIODRIVER': 'alsa',
                'LD_LIBRARY_PATH': ld_library_path,
            },
        )
