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

import asyncio
from typing import TYPE_CHECKING

from batocera_launch.command import Command

if TYPE_CHECKING:
    from pathlib import Path


async def test_commands_reach_the_emulator_through_its_pipe(tmp_path: Path) -> None:
    pipe = tmp_path / 'commands'
    command = Command(['sh', '-c', 'read line; [ "$line" = "LOAD_STATE_SLOT 3" ]'], stdin_pipe=pipe)

    async def send() -> None:
        while not pipe.exists():
            await asyncio.sleep(0.01)
        await asyncio.to_thread(pipe.write_text, 'LOAD_STATE_SLOT 3\n')

    exit_code, _ = await asyncio.gather(command.run(), send())

    assert exit_code == 0
    assert not pipe.exists()
