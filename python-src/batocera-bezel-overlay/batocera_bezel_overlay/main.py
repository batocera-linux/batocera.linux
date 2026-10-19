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

import os
import sys


def _run(session_type: str, /) -> int:
    from batocera_bezel_overlay.app import Application

    app = Application(session_type)
    return app.run(sys.argv)


def main() -> int:
    # Force GDK backend selection before initializing GTK/GDK modules
    session_type = os.environ.get('XDG_SESSION_TYPE', 'x11').lower()

    if 'wayland' in session_type:
        os.environ['GDK_BACKEND'] = 'wayland'
    elif 'x11' in session_type:
        os.environ['GDK_BACKEND'] = 'x11'

    try:
        return _run(session_type)
    except KeyboardInterrupt:
        return 0
