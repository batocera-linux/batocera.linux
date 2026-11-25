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

"""batocera-launch-savestate save [-1] | load [<slot>]: asks the running game's launcher.

Exits 0 when done, 2 when the emulator has no state handling, 3 when only restarting the game
loads that state, and 1 when no launcher answers.
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path
from typing import Final

SOCKET_PATH: Final = Path('/run/batocera-launch/savestates.sock')
NO_LAUNCHER: Final = 1


def request(*words: str, path: Path = SOCKET_PATH) -> int:
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(10)
            connection.connect(str(path))
            connection.sendall(' '.join(words).encode())
            reply = connection.makefile().readline()
    except OSError:
        return NO_LAUNCHER

    try:
        return int(reply)
    except ValueError:
        return NO_LAUNCHER


def main() -> None:
    if not 2 <= len(sys.argv) <= 3 or sys.argv[1] not in ('save', 'load'):
        print(f'usage: {Path(sys.argv[0]).name} save [-1] | load [<slot>]', file=sys.stderr)
        sys.exit(NO_LAUNCHER)

    sys.exit(request(*sys.argv[1:]))
