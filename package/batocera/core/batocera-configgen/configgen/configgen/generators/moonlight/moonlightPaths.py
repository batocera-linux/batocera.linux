from __future__ import annotations

from typing import Final

from ...batoceraPaths import CONFIGS

MOONLIGHT_CONFIG_DIR: Final = CONFIGS / 'moonlight'
MOONLIGHT_CONFIG: Final = MOONLIGHT_CONFIG_DIR / 'moonlight.conf'
MOONLIGHT_GAME_LIST: Final = MOONLIGHT_CONFIG_DIR / 'gamelist.txt'
MOONLIGHT_STAGING_DIR: Final = MOONLIGHT_CONFIG_DIR / 'staging'
MOONLIGHT_STAGING_CONFIG: Final = MOONLIGHT_STAGING_DIR / 'moonlight.conf'
