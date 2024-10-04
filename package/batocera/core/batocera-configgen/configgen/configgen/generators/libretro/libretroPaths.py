from __future__ import annotations

from pathlib import Path
from typing import Final

from ...batoceraPaths import CONF_INIT, CONFIGS

RETROARCH_CONFIG: Final = CONFIGS / 'retroarch'
RETROARCH_CUSTOM: Final = RETROARCH_CONFIG / 'retroarchcustom.cfg'
RETROARCH_CORE_CUSTOM: Final = RETROARCH_CONFIG / 'cores' / 'retroarch-core-options.cfg'
RETROARCH_OVERLAY_CONFIG: Final = RETROARCH_CONFIG / 'overlay.cfg'

RETROARCH_BIN: Final = Path("/usr/bin/retroarch")

RETROARCH_ROOT_INIT: Final = CONF_INIT / 'retroarch'
RETROARCH_CORES: Final = Path("/usr/lib/libretro")
RETROARCH_SHARE: Final = Path("/usr/share/libretro")
