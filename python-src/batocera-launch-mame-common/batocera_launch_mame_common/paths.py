from __future__ import annotations

from pathlib import Path
from typing import Final

from batocera_common.paths import BIOS, CHEATS, CONFIGS, ROMS, SAVES
from batocera_launch.paths import LAUNCH_DATA_DIR

MAME_BIN_DIR: Final = Path('/usr/bin/mame')
MAME_DATA_DIR: Final = LAUNCH_DATA_DIR / 'mame'


class MAMEPathsMixin:
    @property
    def roms_dir(self) -> Path:
        return ROMS / 'mame'

    @property
    def bios_dir(self) -> Path:
        return BIOS / 'mame'

    @property
    def config_dir(self) -> Path:
        return CONFIGS / 'mame'

    @property
    def saves_dir(self) -> Path:
        return SAVES / 'mame'

    @property
    def cheats_dir(self) -> Path:
        return CHEATS / 'mame'
