from __future__ import annotations

from typing import Final

from ...batoceraPaths import BIOS, CHEATS, CONFIGS, DEFAULTS_DIR, ROMS, SAVES

MAME_CONFIG: Final = CONFIGS / "mame"
MAME_SAVES: Final = SAVES / "mame"
MAME_BIOS: Final = BIOS / "mame"
MAME_CHEATS: Final = CHEATS / "mame"
MAME_ROMS: Final = ROMS / "mame"
MAME_DEFAULT_DATA: Final = DEFAULTS_DIR / "data" / "mame"
