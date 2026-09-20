from __future__ import annotations

from pathlib import Path
from typing import Final

from batocera_launch.paths import LAUNCH_DATA_DIR

MAME_BIN_DIR: Final = Path('/usr/bin/mame')
MAME_DATA_DIR: Final = LAUNCH_DATA_DIR / 'mame'
