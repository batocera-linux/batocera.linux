from __future__ import annotations

from pathlib import Path
from typing import Final

from batocera_common.paths import BIOS, CHEATS, CONFIGS, ROMS, SAVES
from batocera_launch.paths import DEFAULTS_DIR

MAME_CONFIG: Final = CONFIGS / 'mame'
MAME_SAVES: Final = SAVES / 'mame'
MAME_BIOS: Final = BIOS / 'mame'
MAME_CHEATS: Final = CHEATS / 'mame'
MAME_ROMS: Final = ROMS / 'mame'
MAME_BIN_DIR: Final = Path('/usr/bin/mame')
MAME_DEFAULT_DATA: Final = DEFAULTS_DIR / 'data' / 'mame'
