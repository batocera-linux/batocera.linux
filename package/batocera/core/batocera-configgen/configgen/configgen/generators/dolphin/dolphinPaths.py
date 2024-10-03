from __future__ import annotations

from typing import Final

from ...batoceraPaths import BIOS, CONFIGS, SAVES

DOLPHIN_CONFIG: Final = CONFIGS / "dolphin-emu"
DOLPHIN_INI: Final = DOLPHIN_CONFIG / "Dolphin.ini"
DOLPHIN_GFX_INI: Final = DOLPHIN_CONFIG / "GFX.ini"
DOLPHIN_QT_INI: Final = DOLPHIN_CONFIG / "Qt.ini"

DOLPHIN_SAVES: Final = SAVES / "dolphin-emu"
DOLPHIN_SYSCONF: Final = DOLPHIN_SAVES / "Wii" / "shared2" / "sys" / "SYSCONF"

DOLPHIN_BIOS: Final = BIOS / "GC"
