from __future__ import annotations

from pathlib import Path
from typing import Final

from ...batoceraPaths import CONFIGS, SAVES

XEMU_BIN: Final = Path('/usr/bin/xemu')
XEMU_SAVES: Final = SAVES / 'xbox'
XEMU_CONFIG: Final = CONFIGS / 'xemu' / 'xemu.toml'
