from __future__ import annotations

from pathlib import Path
from typing import Final

from batocera_common.paths import CONFIGS

PID_FILE: Final = Path('/var/run/hotkeygen.pid')
CONTEXT_FILE: Final = Path('/var/run/hotkeygen.context')

CONFIG_USERDIR: Final = CONFIGS / 'hotkeygen'
CONFIG_SYSTEMDIR: Final = Path('/usr/share/hotkeygen')
CONFIG_DEFAULTDIR: Final = Path('/etc/hotkeygen')

SYSTEM_DEFAULT_MAPPING: Final = CONFIG_DEFAULTDIR / 'default_mapping.conf'

DEVICE_NAME: Final = 'batocera hotkeys'
