from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Final

import evdev
from evdev import ecodes

from batocera_common.paths import CONFIGS

if TYPE_CHECKING:
    import pyudev

CONFIG_USERDIR: Final = CONFIGS / 'hotkeygen'
CONFIG_SYSTEMDIR: Final = Path('/usr/share/hotkeygen')
CONFIG_DEFAULTDIR: Final = Path('/etc/hotkeygen')
HOTKEYGEN_MAPPING: Final = CONFIG_DEFAULTDIR / 'default_mapping.conf'
DEVICE_NAME: Final = 'batocera hotkeys'

ECODES_NAMES: Final = {
    # add BTN_ to that joysticks buttons can run hotkeys (but keep generating only KEY_ events)
    key_code: key_name
    for key_name, key_code in ecodes.ecodes.items()
    if key_name.startswith(('KEY_', 'BTN_'))
}


def get_input_device(udev_device: pyudev.Device, /) -> evdev.InputDevice[str] | None:
    """Get the input device path for a given udev device."""
    if udev_device.device_node is not None and udev_device.device_node.startswith('/dev/input/event'):
        input_device = evdev.InputDevice(udev_device.device_node)
        returned = False

        try:
            if input_device.name != DEVICE_NAME:
                capabilities = input_device.capabilities()

                if ecodes.EV_KEY in capabilities:
                    returned = True
                    return input_device
        finally:
            if not returned:
                input_device.close()

    return None


def get_device_config_filename(device: evdev.InputDevice[str]) -> str:
    name = re.sub(r'[^a-zA-Z0-9_]', '', device.name.replace(' ', '_'))
    return f'{name}-{device.info.vendor:02x}-{device.info.product:02x}.mapping'
