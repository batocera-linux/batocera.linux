"""batocera-discord: controller-driven Discord voice panel for Batocera.

batocera-discord run           the service (started by /usr/share/batocera/services/discord)
batocera-discord toggle        open or close the panel (for a hotkeygen action or a script)
batocera-discord demo <dir>    render the panel with sample data to PNG files
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog='batocera-discord', description='Discord voice panel for Batocera')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('run', help='run the service')
    commands.add_parser('toggle', help='open or close the panel')
    demo = commands.add_parser('demo', help='render screenshots with sample data')
    demo.add_argument('directory', type=Path)
    demo.add_argument('--language', default='en')
    args = parser.parse_args(argv)

    if args.command == 'toggle':
        from .daemon import send_toggle

        return send_toggle()
    if args.command == 'demo':
        from .demo import render_demo

        return render_demo(args.directory, args.language)
    from .daemon import run_daemon

    return run_daemon()


if __name__ == '__main__':
    sys.exit(main())
