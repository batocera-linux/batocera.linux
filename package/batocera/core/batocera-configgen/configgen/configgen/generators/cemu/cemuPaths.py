from __future__ import annotations

from pathlib import Path
from typing import Final

from ...batoceraPaths import BIOS, CONFIGS, ROMS, SAVES

CEMU_CONFIG: Final  = CONFIGS / 'cemu'
CEMU_ROMDIR: Final = ROMS / 'wiiu'
CEMU_SAVES: Final = SAVES / 'wiiu'
CEMU_BIOS: Final = BIOS / 'cemu'
CEMU_DATA_DIR: Final = Path('/usr/bin/cemu')
CEMU_CONTROLLER_PROFILES: Final = CONFIGS / 'cemu' / 'controllerProfiles'
