from __future__ import annotations

from typing import Final

from ...batoceraPaths import CONFIGS, SAVES

DOLPHIN_TRIFORCE_CONFIG: Final = CONFIGS / "dolphin-triforce"
DOLPHIN_TRIFORCE_INI: Final = DOLPHIN_TRIFORCE_CONFIG / "Config" / "Dolphin.ini"
DOLPHIN_TRIFORCE_GFX_INI: Final = DOLPHIN_TRIFORCE_CONFIG / "Config" / "gfx_opengl.ini"
DOLPHIN_TRIFORCE_LOGGER_INI: Final = DOLPHIN_TRIFORCE_CONFIG / "Config" / "Logger.ini"
DOLPHIN_TRIFORCE_GAME_SETTINGS: Final = DOLPHIN_TRIFORCE_CONFIG / "GameSettings"

DOLPHIN_TRIFORCE_SAVES: Final = SAVES / "dolphin-triforce"
