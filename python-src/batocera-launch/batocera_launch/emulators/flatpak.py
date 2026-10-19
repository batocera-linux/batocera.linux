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

from batocera_common.asyncio import run
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import Command, Emulator, HotkeysContext


@cached_dataclass
class Flatpak(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'flatpak',
            'keys': {
                'exit': 'export XDG_RUNTIME_DIR=/var/run; flatpak kill $(flatpak ps --columns=application | head -n 1)'
            },
        }

    @property
    def needs_mouse(self) -> bool:
        return True

    async def configure(self) -> Command:
        rom_id = self.rom.read_text().strip()

        # bad hack in a first time to get audio for user batocera
        await run('chown', '-R', 'root:audio', '/var/run/pulse', check=False)
        await run('chmod', '-R', 'g+rwX', '/var/run/pulse', check=False)

        return Command(
            ['/usr/bin/flatpak', 'run', '-v', rom_id],
            env={'SDL_JOYSTICK_HIDAPI_XBOX': '0'},
        )
