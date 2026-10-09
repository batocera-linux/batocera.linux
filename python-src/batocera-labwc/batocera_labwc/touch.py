from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from batocera_common.key_value_config import KeyValueConfig
from batocera_common.paths import BATOCERA_CONF
from batocera_common.settings import get_master_section, get_master_setting

if TYPE_CHECKING:
    from collections.abc import Sequence

_logger = logging.getLogger(__name__)

BATOCERA_RESOLUTION: Final = '/usr/bin/batocera-resolution'
BATOCERA_SETTINGS_SET: Final = '/usr/bin/batocera-settings-set'
LIBINPUT: Final = '/usr/bin/libinput'

_DEVICE_RE: Final = re.compile(r'^Device:\s+(.+?)\s*$', re.MULTILINE)
_CAPABILITIES_RE: Final = re.compile(r'^Capabilities:\s+(.+?)\s*$', re.MULTILINE)


@dataclass(slots=True, frozen=True)
class TouchMapping:
    device: str
    output: str
    rotation: int | None


def _run(*command: str) -> str:
    try:
        return subprocess.run(command, capture_output=True, check=True, text=True).stdout
    except OSError, subprocess.CalledProcessError:
        _logger.exception('%s failed.', command[0])
        return ''


def touchscreens() -> list[str]:
    names: list[str] = []

    for block in _run(LIBINPUT, 'list-devices').split('\n\n'):
        device = _DEVICE_RE.search(block)
        capabilities = _CAPABILITIES_RE.search(block)

        if device and capabilities and 'touch' in capabilities.group(1).split():
            names.append(device.group(1))

    return names


def _output_setting(prefix: str, output: str, model: str | None, user_config: KeyValueConfig, /) -> str | None:
    value = get_master_setting(f'{prefix}.{output}', user_config=user_config)

    if value is None and model is not None:
        value = get_master_setting(f'{prefix}.{model}', user_config=user_config)

    return value


def _rotation(value: str | None, /) -> int | None:
    return int(value) if value is not None and value.isdigit() else None


def resolve_touchscreens(outputs: Sequence[str], devices: Sequence[str], /) -> list[TouchMapping]:
    """Map touchscreens to outputs from the display.touchscreen settings, learning the pairing left over when it is the only one."""
    user_config = KeyValueConfig(BATOCERA_CONF)
    models = {
        output: _run(BATOCERA_RESOLUTION, '--screen', output, 'outputModel').strip() or None for output in outputs
    }

    mappings: list[TouchMapping] = []
    for output in outputs:
        device = _output_setting('display.touchscreen', output, models[output], user_config)

        if device is None:
            continue

        rotation = _rotation(_output_setting('display.touchrotate', output, models[output], user_config))
        mappings.append(TouchMapping(device, output, rotation))
        state = '' if device in devices else ' (not connected)'
        print(f"Touchscreen '{device}' mapped to output {output}{state}.")

    if not devices:
        print('No touchscreen found.')
        return mappings

    # a touchscreen configured for an output that is not in the layout is not up for grabs
    configured = set(get_master_section('display.touchscreen', user_config=user_config).values())
    for device in devices:
        if device in configured and all(mapping.device != device for mapping in mappings):
            print(f"Touchscreen '{device}' is configured for an output that is not active.")

    unmapped = [device for device in devices if device not in configured]
    unclaimed = [output for output in outputs if all(mapping.output != output for mapping in mappings)]

    if not unmapped:
        return mappings

    if len(unmapped) == 1 and len(unclaimed) == 1:
        device, output = unmapped[0], unclaimed[0]
        # keyed by the EDID model when there is one, so a different display on the same connector is not matched
        key = models[output] or output
        _run(BATOCERA_SETTINGS_SET, f'display.touchscreen.{key}', device)
        rotation = _rotation(_output_setting('display.touchrotate', output, models[output], user_config))
        mappings.append(TouchMapping(device, output, rotation))
        print(f"Touchscreen '{device}' learnt for output {output} as display.touchscreen.{key}.")
    elif len(unmapped) == 1 and not any(mapping.output == outputs[0] for mapping in mappings):
        # several outputs appeared with the touchscreen, so nothing can be learnt
        mappings.append(TouchMapping(unmapped[0], outputs[0], None))
        print(f"Touchscreen '{unmapped[0]}' cannot be told apart between {', '.join(unclaimed)}; using {outputs[0]}.")
    else:
        print(f'Touchscreens {", ".join(unmapped)} left unmapped. Use sdl2-touch-test to calibrate them.')

    return mappings
