from __future__ import annotations

from typing import Final

from ...batoceraPaths import CONF_INIT, CONFIGS

PPSSPP_CONFIG_DIR: Final = CONFIGS / 'ppsspp'
PPSSPP_PSP_SYSTEM_DIR: Final = PPSSPP_CONFIG_DIR / 'PSP' / 'SYSTEM'
PPSSPP_CONFIG_INIT: Final = CONF_INIT / 'ppsspp' / 'PSP' / 'SYSTEM'
