from __future__ import annotations

from typing import Final

from batocera_common.paths import CONFIGS, SAVES
from batocera_launch.paths import DATAINIT_DIR

# These deliberately don't match the emulator's own launch name ("mupen64plus") -
# kept as the historical directory name ("mupen64") so existing users' configs,
# input mappings and save states aren't silently relocated.
MUPEN64PLUS_CONFIG: Final = CONFIGS / 'mupen64'
MUPEN64PLUS_CUSTOM_CFG: Final = MUPEN64PLUS_CONFIG / 'mupen64plus.cfg'
MUPEN64PLUS_USER_MAPPING: Final = MUPEN64PLUS_CONFIG / 'input.xml'
MUPEN64PLUS_SYSTEM_MAPPING: Final = DATAINIT_DIR / 'system' / 'configs' / 'mupen64' / 'input.xml'

MUPEN64PLUS_SAVES: Final = SAVES / 'n64'
