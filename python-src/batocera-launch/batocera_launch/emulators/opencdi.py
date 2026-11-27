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
from batocera_common.paths import BIOS, SCREENSHOTS
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path

# per console: system rom, digital video cartridge rom, nvram file
_BOARDS: Final = {
    'mono1': ('cdimono1.zip', 'vmpega.rom', 'nvram_mk48t08.bin'),
    'mono4': ('cdi490a.zip', 'impega.rom', 'nvram_cdi490a.bin'),
}


@cached_dataclass
class OpenCDI(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'opencdi',
            'keys': {
                'exit': 'KEY_ESC',
                'pause': 'KEY_P',
                'reset': 'KEY_F5',
                'screenshot': 'KEY_F8',
                'fastforward': 'KEY_SPACE',
            },
        }

    # opencdi keeps its ini files in the working directory, entered before configure
    @property
    def execution_path(self) -> Path | None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        return self.config_dir

    async def configure(self) -> Command:
        states_dir = self.saves_dir / 'opencdi'
        states_dir.mkdir(parents=True, exist_ok=True)

        board = self.config.get_str('opencdi_board', 'mono1')
        rom, dvc, nvram = _BOARDS.get(board, _BOARDS['mono1'])

        args: list[str | Path] = [
            'opencdi',
            '--fullscreen',
            '--no-menu',
            '--board',
            board,
            '--rom',
            BIOS / rom,
            '--nvram',
            states_dir / nvram,
            '--states-dir',
            states_dir,
            '--screenshot-dir',
            SCREENSHOTS,
            '--audio-latency',
            self.config.get_str('opencdi_audio_latency', 'normal'),
        ]
        if not self.config.get_bool('opencdi_dvc', True):
            args.append('--no-dvc')
        elif (BIOS / dvc).exists():
            args.extend(['--dvc', BIOS / dvc])
        if not self.config.get_bool('opencdi_autoplay', True):
            args.append('--no-autoplay')
        if self.config.get_bool('opencdi_deinterlace'):
            args.append('--deinterlace')
        args.append(self.rom)

        # opencdi logs every disc sector at its default level
        return Command(args, env={'RUST_LOG': 'warn'})
