from __future__ import annotations

from typing import Final

from ...batoceraPaths import BIOS, CHEATS, CONFIGS, DEFAULTS_DIR, ROMS, SAVES

MAME_CONFIG: Final = CONFIGS / "mame"
MAME_SAVES: Final = SAVES / "mame"
MAME_BIOS: Final = BIOS / "mame"
MAME_CHEATS: Final = CHEATS / "mame"
MAME_ROMS: Final = ROMS / "mame"
MAME_DEFAULT_DATA: Final = DEFAULTS_DIR / "data" / "mame"

MESS_ROMS: Final = ROMS / "mess"
MESS_SOFTLIST_MAP: Final = MAME_DEFAULT_DATA / "messSoftlistMap.json"
MESS_SYSTEMS_MAPPING: Final = MAME_DEFAULT_DATA / "messSystems.json"
MESS_AUTOBOOT_SCRIPTS: Final = MAME_DEFAULT_DATA / "autoboot_scripts"
MESS_HASH_CACHE: Final = MAME_SAVES / "mess_hash_cache.json"
MAME_HASH_DIR: Final = MAME_BIOS / "hash"
