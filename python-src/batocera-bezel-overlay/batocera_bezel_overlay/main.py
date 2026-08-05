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
