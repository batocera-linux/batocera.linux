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

from typing import Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import Command, Emulator, HotkeysContext

# AppleWin's own hard-disk image formats
# everything else accepted by the apple2 system (nib/do/po/dsk/mfi/dfi/rti/edd/woz/wav/zip/7z)
# is a floppy image, loaded via --d1.
_HARD_DISK_EXTENSIONS: Final = {'.hdv', '.2mg'}


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
        config_file = self.config_dir / 'applewin.yaml'
        config_file.touch(exist_ok=True)

        disk_flag = '--h1' if self.rom.suffix.lower() in _HARD_DISK_EXTENSIONS else '--d1'

        return Command(['applewin', '--fullscreen', '--conf', config_file, disk_flag, self.rom])
