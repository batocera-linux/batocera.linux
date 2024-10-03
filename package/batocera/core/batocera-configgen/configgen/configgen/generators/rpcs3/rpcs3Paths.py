from __future__ import annotations

from pathlib import Path
from typing import Final

from ...batoceraPaths import CONFIGS

RPCS3_CONFIG_DIR: Final = CONFIGS / 'rpcs3'
RPCS3_CONFIG: Final = RPCS3_CONFIG_DIR / 'config.yml'
RPCS3_CURRENT_CONFIG: Final = RPCS3_CONFIG_DIR / 'GuiConfigs' / 'CurrentSettings.ini'
RPCS3_CONFIG_INPUT: Final = RPCS3_CONFIG_DIR / 'config_input.yml'
RPCS3_CONFIG_EVDEV: Final = RPCS3_CONFIG_DIR / 'InputConfigs' / 'Evdev' / 'Default Profile.yml'
RPCS3_BIN: Final = Path('/usr/bin/rpcs3')
