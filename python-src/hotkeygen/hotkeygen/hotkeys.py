from __future__ import annotations

import argparse
import datetime
import errno
import json
import os
import re
import select
import sys
from typing import TYPE_CHECKING, Literal, TypedDict

import evdev
import pyudev
from evdev import ecodes

from hotkeygen.shared import CONFIG_SYSTEMDIR, CONFIG_USERDIR, ECODES_NAMES, HOTKEYGEN_MAPPING

if TYPE_CHECKING:
    from pathlib import Path

DEVICES_EXCLUSION = ['batocera hotkeys']


def add_devices(
    poll: select.poll, udev_context: pyudev.Context, device_path: str | None, gdebug: bool
) -> dict[int, evdev.InputDevice]:
    input_devices_by_fd: dict[int, evdev.InputDevice] = {}
    # filter devices to add
    for device in udev_context.list_devices(subsystem='input'):
        if (
            device.device_node is not None
            and device.device_node.startswith('/dev/input/event')
            and (device_path is None or device_path == device.device_node)
        ):
            input_device = evdev.InputDevice(device.device_node)
            if input_device.name not in DEVICES_EXCLUSION:
                capabilities = input_device.capabilities()
                if ecodes.EV_KEY in capabilities:
                    if gdebug:
                        print(f'listening device {device.device_node:<18} {input_device.name}', file=sys.stderr)
                    input_devices_by_fd[input_device.fileno()] = input_device
                    poll.register(input_device, select.POLLIN)
    return input_devices_by_fd


def remove_devices(poll: select.poll, input_devices_by_fd: dict[int, evdev.InputDevice]) -> None:
    for fd in list(input_devices_by_fd):
        input_device = input_devices_by_fd[fd]
        del input_devices_by_fd[fd]
        try:
            poll.unregister(input_device)
            input_device.close()
        except:  # noqa: E722
            pass


class _PressureInfo(TypedDict):
    name: str
    config: str
    keys: dict[str, dict[str, int]]


type _Pressures = dict[str | bytes, _PressureInfo]


def handle_event(
    device: evdev.InputDevice,
    event: evdev.InputEvent,
    pressures: dict[str | bytes, _PressureInfo],
    nowait: bool,
    gdebug: bool,
) -> bool:
    if event.type == ecodes.EV_KEY:
        config_name = get_device_config_filename(device)
        if event.code in ECODES_NAMES:
            code_name = ECODES_NAMES[event.code]
            if gdebug:
                print(f'{device.path:<20} {code_name:<16} {device.name:<40} {config_name}', file=sys.stderr)
            if device.path not in pressures:
                pressures[device.path] = {'name': device.name, 'config': config_name, 'keys': {}}
            if code_name not in pressures[device.path]['keys']:
                pressures[device.path]['keys'][code_name] = {'count': 0}
            pressures[device.path]['keys'][code_name]['count'] += 1
            if not nowait:
                os.system("batocera-flash-screen 0.1 '#ff00ff'")
            return True
    return False


def do_output(pressures: _Pressures, ncount: int, evformat: bool) -> None:
    if not sys.stdout.isatty():
        print('<keys>')
    for evt in pressures:
        for key in pressures[evt]['keys']:
            if pressures[evt]['keys'][key]['count'] == ncount:
                key_str = key
                if evformat:
                    key_str = udevtoevcode(key)
                if sys.stdout.isatty():
                    print(f'{evt:<20} {key_str:<16} {pressures[evt]["name"]:<40} {pressures[evt]["config"]}')
                else:
                    print(
                        f'<key event="{evt}" key="{key_str}" config="{pressures[evt]["config"]}" count="{pressures[evt]["keys"][key]["count"]}" />'
                    )
    if not sys.stdout.isatty():
        print('</keys>')


def do_detect(ncount: int, duration: int, device_path: str, nowait: bool, evformat: bool, gdebug: bool) -> None:
    udev_context = pyudev.Context()
    poll = select.poll()
    input_devices_by_fd = add_devices(poll, udev_context, device_path, gdebug)
    start_time = datetime.datetime.now()
    pressures: _Pressures = {}

    # read all devices
    if sys.stdout.isatty():
        print(f'Press {ncount} times buttons to filter', file=sys.stderr)

    foundOne = False
    while datetime.datetime.now() - start_time < datetime.timedelta(seconds=duration) and (
        (nowait and foundOne == 0) or (not nowait)
    ):
        try:
            for fd, _ in poll.poll(100):
                try:
                    event = input_devices_by_fd[fd].read_one()
                    if (
                        event is not None
                        and event.type == ecodes.EV_KEY
                        and event.value == 1
                        and handle_event(input_devices_by_fd[fd], event, pressures, nowait, gdebug)
                    ):
                        foundOne = True
                except Exception as e:
                    # error on a single device
                    if fd in input_devices_by_fd:
                        input_device = input_devices_by_fd[fd]
                        if not (isinstance(e, OSError) and e.errno == errno.ENODEV):
                            print(e)
                            print(f'error on device {input_device.name} ({input_device.path}), closing.')
                        del input_devices_by_fd[fd]
                        try:
                            poll.unregister(input_device)
                            input_device.close()
                        except:  # noqa: E722
                            pass
        except KeyboardInterrupt:
            remove_devices(poll, input_devices_by_fd)
            return
    remove_devices(poll, input_devices_by_fd)
    do_output(pressures, ncount, evformat)


def getConfigFancyName(file: str) -> str:
    # remove the vip/pid, extension and replace _ by spaces
    x = re.sub(r'-[^-]*-[^-]*\.mapping', '', file.replace('_', ' '))
    # replace multiple spaces by single ones
    x = re.sub('[ ]+', ' ', x)
    return x.strip()


class _ConfigFileInfo(TypedDict):
    path: Path
    source: Literal['system', 'user']


def getAllConfigFiles() -> dict[str, _ConfigFileInfo]:
    res: dict[str, _ConfigFileInfo] = {}
    for XCONFIG in [CONFIG_SYSTEMDIR, CONFIG_USERDIR]:
        if XCONFIG.exists():
            source = 'system'
            if XCONFIG == CONFIG_USERDIR:
                source = 'user'
            for file in XCONFIG.iterdir():
                if file.is_file() and file.suffix == '.mapping':
                    res[file.name] = {'path': file, 'source': source}
    return res


def get_device_config_filename(device: evdev.InputDevice) -> str:
    name = re.sub('[^a-zA-Z0-9_]', '', device.name.replace(' ', '_'))
    return f'{name}-{device.info.vendor:02x}-{device.info.product:02x}.mapping'


def getConfigsFromConnectedDevices() -> set[str]:
    res: set[str] = set()
    udev_context = pyudev.Context()
    for device in udev_context.list_devices(subsystem='input'):
        if device.device_node is not None and device.device_node.startswith('/dev/input/event'):
            dev = evdev.InputDevice(device.device_node)
            res.add(get_device_config_filename(dev))
    return res


# to avoid listing all systems hotkeys (like almost nobody want to see the steamdeck hotkeys)
# filter list to existing devices
def do_list():
    required_configs = getConfigsFromConnectedDevices()

    n = 0
    if not sys.stdout.isatty():
        print('<hotkeys>')
    configs = getAllConfigFiles()
    for file, infos in configs.items():
        # remove system configs from not connected devices
        if infos['source'] == 'system' and file not in required_configs:
            continue
        values = {}
        with infos['path'].open() as fd:
            values = json.load(fd)
        fancy_name = getConfigFancyName(file)

        if sys.stdout.isatty():
            if n != 0:
                print('')
            print(f'{fancy_name} ({file})')
            for key in values:
                action = values[key]
                print(f'  {key:<16} {action:<16}')
        else:
            print(f'  <device fancy_name="{fancy_name}" config="{file}">')
            for key in values:
                action = values[key]
                print(f'    <hotkey key="{key}" action="{action}" />')
            print('  </device>')
        n = n + 1
    if not sys.stdout.isatty():
        print('</hotkeys>')


def do_set(config: str, key: str, action: str | None) -> None:
    if not config.endswith('.mapping'):
        print('invalid configuration file', file=sys.stderr)
        return

    userpath = CONFIG_USERDIR / config
    systempath = CONFIG_SYSTEMDIR / config
    values = {}

    # read the user file. if not, ready the system file (but always write in the user file)
    if userpath.is_file():
        with userpath.open() as fd:
            values = json.load(fd)
    elif systempath.is_file():
        with systempath.open() as fd:
            values = json.load(fd)

    if action == 'none':
        values[key] = ''
    elif action is None:
        if key in values:
            del values[key]
    else:
        values[key] = action
    if not CONFIG_USERDIR.exists():
        CONFIG_USERDIR.mkdir(parents=True)
    with userpath.open('w') as fd:
        json.dump(values, fd, indent=4)


def udevtoevcode(code: str) -> str:
    if code[0:4] == 'KEY_':
        return 'key:' + code[4:].lower()
    if code[0:4] == 'BTN_':
        return 'btn:' + code[4:].lower()
    if code[0:4] == 'ABS_':
        return 'abs:' + code[4:].lower()
    return code


def list_values(hotkeys_mapping: _HotkeyMapping) -> None:
    print('<mapping>')
    for key in sorted(hotkeys_mapping['by_names']):
        value = hotkeys_mapping['by_names'][key]
        evvalue = udevtoevcode(value)
        print(f'<key code="{value}" evcode="{evvalue}" name="{key}" />')
    print('</mapping>')


class _HotkeyMapping(TypedDict):
    by_keys: dict[str, str]
    by_names: dict[str, str]


def read_hotkey_mapping(hotkey_mapping_file: Path) -> _HotkeyMapping:
    mapping = json.loads(hotkey_mapping_file.read_text())
    by_keys: dict[str, str] = mapping
    by_names: dict[str, str] = {}
    for m in by_keys:
        by_names[by_keys[m]] = m
    return {'by_keys': by_keys, 'by_names': by_names}


def main() -> None:
    parser = argparse.ArgumentParser(prog='batocera-hotkeys')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--count', type=int, help='detection count')
    parser.add_argument('--duration', type=int, help='detection duration')
    parser.add_argument('--detect', action='store_true')
    parser.add_argument('--values', action='store_true')
    parser.add_argument('--set', action='store_true')
    parser.add_argument('--remove', action='store_true')
    parser.add_argument('--config', type=str, help='config to set')
    parser.add_argument('--key', type=str, help='key to set')
    parser.add_argument('--action', type=str, help='action to set')
    parser.add_argument('--device', type=str, help='device to filter on detection')
    parser.add_argument('--nowait', action='store_true', help='no wait on detection')
    parser.add_argument('--evformat', action='store_true', help='ev format')
    args = parser.parse_args()

    ncount = 2
    duration = 4  # x seconds
    nowait = False
    evformat = False
    gdebug = False

    if args.debug:
        gdebug = True
    if args.count:
        ncount = args.count
    if args.duration:
        duration = args.duration
    if args.nowait:
        nowait = True
    if args.evformat:
        evformat = True

    if args.detect:
        do_detect(ncount, duration, args.device, nowait, evformat, gdebug)
    elif args.values:
        hotkeys_mapping = read_hotkey_mapping(HOTKEYGEN_MAPPING)
        list_values(hotkeys_mapping)
    elif args.remove:
        if args.config and args.key:
            do_set(args.config, args.key, None)
            os.system('hotkeygen --reload')  # reload the configuration
        else:
            print('remove requires config and key arguments', file=sys.stderr)
    elif args.set:
        if args.config and args.key and args.action:
            do_set(args.config, args.key, args.action)
            os.system('hotkeygen --reload')  # reload the configuration
        else:
            print('set requires config, key and action arguments', file=sys.stderr)
    else:
        do_list()
