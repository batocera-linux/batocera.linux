from __future__ import annotations

from typing import TYPE_CHECKING, Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path

_CD_SUFFIXES: Final = {'.iso', '.cue', '.bin'}


@cached_dataclass
class Tsugaru(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'tsugaru',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4'], 'menu': 'KEY_F10', 'pause': 'KEY_F10'},
        }

    async def configure(self) -> Command:
        args: list[str | Path] = [
            '/usr/bin/Tsugaru_CUI',
            BIOS / 'fmtowns',
            '-FULLSCREEN',
            '-NOHIGHRESPCM',
            '-NOWAITBOOT',
            '-AUTOSCALE',
            '-MAINTAINASPECT',
            '-HIGHRES',
            '-GAMEPORT0',
            'KEY',
            '-KEYBOARD',
            'DIRECT',
            '-PAUSEKEY',
            'F10',
        ]

        if (cdrom_speed := self.config.get_str('cdrom_speed', 'auto')) != 'auto':
            args.extend(['-CDSPEED', cdrom_speed])

        if self.config.get_bool('386dx'):
            args.append('-PRETEND386DX')

        if self.rom.suffix.lower() in _CD_SUFFIXES:
            args.extend(['-CD', self.rom])
        else:
            args.extend(['-FD0', self.rom])

        return Command(args)
