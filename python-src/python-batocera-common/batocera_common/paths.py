from __future__ import annotations

from pathlib import Path
from typing import Final

BATOCERA_SHARE_DIR: Final = Path('/usr/share/batocera')
USERDATA: Final = Path('/userdata')

HOME: Final = USERDATA / 'system'
CONFIGS: Final = HOME / 'configs'
SAVES: Final = USERDATA / 'saves'
SCREENSHOTS: Final = USERDATA / 'screenshots'
RECORDINGS: Final = USERDATA / 'recordings'
BIOS: Final = USERDATA / 'bios'
OVERLAYS: Final = USERDATA / 'overlays'
CACHE: Final = HOME / 'cache'
ROMS: Final = USERDATA / 'roms'
CHEATS: Final = USERDATA / 'cheats'
LOGS: Final = HOME / 'logs'
BATOCERA_CONF: Final = HOME / 'batocera.conf'

SQUASHFS_DIR: Final = Path('/var/run/squashfs')
ROM_OVERLAY_DIR: Final = Path('/var/run/overlays')
