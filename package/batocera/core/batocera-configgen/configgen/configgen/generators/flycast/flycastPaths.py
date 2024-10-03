from __future__ import annotations

from typing import Final

from ...batoceraPaths import BIOS, CONFIGS, DEFAULTS_DIR, SAVES

FLYCAST_CONFIG_DIR: Final = CONFIGS / 'flycast'
FLYCAST_MAPPING: Final = FLYCAST_CONFIG_DIR / 'mappings'
FLYCAST_CONFIG: Final = FLYCAST_CONFIG_DIR / 'emu.cfg'
FLYCAST_SAVES: Final = SAVES / 'dreamcast' / 'flycast'
FLYCAST_BIOS: Final = BIOS / 'dc'

FLYCAST_VMU_BLANK: Final = DEFAULTS_DIR / 'data' / 'dreamcast' / 'vmu_save_blank.bin'
FLYCAST_VMUA1: Final = FLYCAST_SAVES / 'vmu_save_A1.bin'
FLYCAST_VMUA2: Final = FLYCAST_SAVES / 'vmu_save_A2.bin'
