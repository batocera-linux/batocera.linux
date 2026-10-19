# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path

_CD_SUFFIXES: Final = {'.iso', '.cue', '.bin'}
_FLOPPY_DRIVES: Final = 2


def _media_args(rom: Path, /) -> list[str | Path]:
    images = [rom]
    if rom.suffix.lower() == '.m3u':
        lines = (line.strip() for line in rom.read_text().splitlines())
        images = [rom.parent / line for line in lines if line and not line.startswith('#')]

    # an m3u can pair a CD with its boot floppy, so each image goes to the drive it fits
    cds = [image for image in images if image.suffix.lower() in _CD_SUFFIXES]
    floppies = [image for image in images if image.suffix.lower() not in _CD_SUFFIXES]
    args: list[str | Path] = []
    for drive, floppy in enumerate(floppies[:_FLOPPY_DRIVES]):
        args.extend([f'-FD{drive}', floppy])
    if cds:
        args.extend(['-CD', cds[0]])
    return args


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

        args.extend(_media_args(self.rom))

        return Command(args)
