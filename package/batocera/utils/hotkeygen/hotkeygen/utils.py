from __future__ import annotations

import asyncio
import json
import os
import re
from typing import TYPE_CHECKING

from batocera_common.paths import existing_files_in_directories

from .paths import (
    CONFIG_DEFAULTDIR,
    CONFIG_SYSTEMDIR,
    CONFIG_USERDIR,
    DEVICE_NAME,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    import evdev
    import pyudev

    from ._types import HotkeysContext, HotkeysContextMapping, KeysDict, KeysMapping


def get_input_device(udev_device: pyudev.Device, /) -> evdev.InputDevice[str] | None:
    """Get the input device path for a given udev device."""
    if udev_device.device_node is not None and udev_device.device_node.startswith('/dev/input/event'):
        import evdev

        input_device = evdev.InputDevice(udev_device.device_node)
        returned = False

        try:
            if input_device.name != DEVICE_NAME:
                capabilities = input_device.capabilities()

                if evdev.ecodes.EV_KEY in capabilities:
                    returned = True
                    return input_device
        finally:
            if not returned:
                input_device.close()

    return None


def get_device_config_filename(device: evdev.InputDevice[str]) -> str:
    name = re.sub(r'[^a-zA-Z0-9_]', '', device.name.replace(' ', '_'))
    return f'{name}-{device.info.vendor:02x}-{device.info.product:02x}.mapping'


def get_device_mapping_path(device: evdev.InputDevice[str] | None, debug: bool) -> Path | None:
    if device is not None:
        filename = get_device_config_filename(device)

        if debug:
            print(f'...looking for {filename} in {CONFIG_USERDIR}, {CONFIG_SYSTEMDIR}')

        for path in existing_files_in_directories(filename, (CONFIG_USERDIR, CONFIG_SYSTEMDIR)):
            return path

    return None


def _load_mapping(data: dict[str, str]) -> dict[int, str]:
    try:
        from evdev import ecodes

        mapping: dict[int, str] = {}
        for key, action in data.items():
            if key in ecodes.ecodes:
                mapping[ecodes.ecodes[key]] = action
            else:
                raise Exception(f'invalid key {key!r}')
        return mapping
    except Exception as e:
        print(f'fail to load mapping : {e}')
        return {}


def get_device_mapping(device: evdev.InputDevice[str] | None, debug: bool) -> dict[int, str]:
    mapping_path = get_device_mapping_path(device, debug)

    if mapping_path is not None:
        if debug:
            print(f'using mapping {mapping_path}')

        data = json.loads(mapping_path.read_text())
        return _load_mapping(data)

    data: dict[str, str] = {}

    for mapping_file in existing_files_in_directories('default_mapping.conf', (CONFIG_DEFAULTDIR, CONFIG_USERDIR)):
        if debug:
            print(f'use mapping file {mapping_file}')

        data |= json.loads(mapping_file.read_text())

    return _load_mapping(data)


async def reset_device(target_device: evdev.UInput, /) -> None:
    from evdev import ecodes

    target_device.write(ecodes.EV_REL, ecodes.REL_X, -10000)
    target_device.write(ecodes.EV_REL, ecodes.REL_Y, -10000)
    target_device.syn()

    await asyncio.sleep(0.10)

    # Only send mouse click on Wayland (unsafe on X11)
    if os.environ.get('WAYLAND_DISPLAY'):
        target_device.write(ecodes.EV_KEY, ecodes.BTN_LEFT, 1)
        target_device.syn()
        target_device.write(ecodes.EV_KEY, ecodes.BTN_LEFT, 0)
        target_device.syn()

        await asyncio.sleep(0.10)


async def reset_mouse() -> None:
    # Create temporary device
    import evdev
    from evdev import ecodes

    sender = evdev.UInput(
        name='batocera-mouse-reset',
        events={ecodes.EV_REL: [ecodes.REL_X, ecodes.REL_Y], ecodes.EV_KEY: [ecodes.BTN_LEFT]},
    )

    try:
        await asyncio.sleep(0.2)

        await reset_device(sender)
    finally:
        sender.close()


def get_common_context_keys() -> KeysDict:
    keys: KeysDict = {}

    for common_file in existing_files_in_directories('common_context.conf', (CONFIG_DEFAULTDIR, CONFIG_USERDIR)):
        keys |= get_keys_dict(json.loads(common_file.read_text()))

    return keys


def get_ecode_name(code: int, /) -> str:
    from evdev import ecodes

    value = ecodes.keys[code]  # ecodes.keys is a combination of all KEY_ and BTN_ codes

    if isinstance(value, str):
        return value

    return value[-1]


def print_context(context: HotkeysContext) -> None:
    print(f'Context [{context["name"]}]:')

    for action, keys in context['keys'].items():
        if isinstance(keys, list):
            print(f'  {action:-<20}-> {[get_ecode_name(key) for key in keys]}')
        elif isinstance(keys, str):
            print(f'  {action:-<20}-> command [{keys}]')
        else:
            print(f'  {action:-<20}-> {get_ecode_name(keys)}')


def print_mapping(
    mapping: Mapping[int, str], associations: Mapping[int, str], /, context: HotkeysContext | None = None
) -> None:
    for k in mapping:
        k_name = get_ecode_name(k)

        if k in associations:
            if context is None:
                print(f'  {k_name:-<15}-> {associations[k]}')
            else:
                if associations[k] in context['keys']:
                    key_codes = context['keys'][associations[k]]
                    if isinstance(key_codes, list):
                        key_names = [get_ecode_name(x) for x in key_codes]
                        print(f'  {k_name:-<15}-> {associations[k]:-<15}-> {key_names}')
                    elif isinstance(key_codes, str):
                        print(f'  {k_name:-<15}-> {associations[k]:-<15}-> {key_codes}')
                    else:
                        print(f'  {k_name:-<15}-> {associations[k]:-<15}-> {get_ecode_name(key_codes)}')
                else:
                    print(f'  {k_name:-<15}-> {associations[k]:15}')


def get_keys_dict(keys: KeysMapping) -> KeysDict:
    from evdev import ecodes

    res: KeysDict = {}

    for action, key_code_names in keys.items():
        if isinstance(key_code_names, str):
            # string are key if starting by KEY_ else commands (maybe not the best choice, but simple)
            if key_code_names.startswith('KEY_'):
                if key_code_names in ecodes.ecodes:
                    res[action] = ecodes.ecodes[key_code_names]
                else:
                    raise Exception(f'invalid key {key_code_names!r}')
            else:
                # command
                res[action] = key_code_names
        else:
            codes: list[int] = []
            res[action] = codes
            for x in key_code_names:
                if x in ecodes.ecodes:
                    codes.append(ecodes.ecodes[x])
                else:
                    raise Exception(f'invalid key {x!r}')

    return res


def get_hotkeys_context(
    data: HotkeysContextMapping, /, include_common: bool = True, *, debug: bool = False
) -> HotkeysContext:
    if 'name' not in data:
        raise Exception('no name section found')
    if 'keys' not in data:
        raise Exception('no keys section found')

    context: HotkeysContext = {'name': data['name'], 'keys': get_keys_dict(data['keys'])}

    if debug:
        print_context(context)

    if include_common:
        context['keys'] |= get_common_context_keys()

    return context
