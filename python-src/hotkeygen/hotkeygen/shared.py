from __future__ import annotations

from pathlib import Path
from typing import Final

from evdev import ecodes

CONFIG_USERDIR: Final = Path('/userdata/system/configs/hotkeygen')
CONFIG_SYSTEMDIR: Final = Path('/usr/share/hotkeygen')
CONFIG_DEFAULTDIR: Final = Path('/etc/hotkeygen')
HOTKEYGEN_MAPPING: Final = CONFIG_DEFAULTDIR / 'default_mapping.conf'

ECODES_NAMES: Final = {
    # add BTN_ to that joysticks buttons can run hotkeys (but keep generating only KEY_ events)
    key_code: key_name
    for key_name, key_code in ecodes.ecodes.items()
    if key_name.startswith(('KEY_', 'BTN_'))
}
