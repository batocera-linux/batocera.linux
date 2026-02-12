from __future__ import annotations

import argparse
import datetime
import errno
import json
import re
import select
import subprocess
import sys
from typing import TYPE_CHECKING, Literal, TypedDict

import evdev
import pyudev
from evdev import ecodes

from .shared import (
    CONFIG_SYSTEMDIR,
    CONFIG_USERDIR,
    ECODES_NAMES,
    HOTKEYGEN_MAPPING,
    get_device_config_filename,
    get_input_device,
)

if TYPE_CHECKING:
    from pathlib import Path


def _add_devices(
    poll: select.poll,
    udev_context: pyudev.Context,
    device_path: str | None,
    debug: bool,
    /,
) -> dict[int, evdev.InputDevice[str]]:
    input_devices_by_fd: dict[int, evdev.InputDevice[str]] = {}

    # filter devices to add
    for device in udev_context.list_devices(subsystem='input'):
        if (device_path is None or device_path == device.device_node) and (
            input_device := get_input_device(device)
        ) is not None:
            if debug:
                print(f'listening device {device.device_node:<18} {input_device.name}', file=sys.stderr)
            input_devices_by_fd[input_device.fileno()] = input_device
            poll.register(input_device, select.POLLIN)

    return input_devices_by_fd


def _remove_devices(
    poll: select.poll,
    input_devices_by_fd: dict[int, evdev.InputDevice[str]],
    /,
) -> None:
    for fd in list(input_devices_by_fd):
        input_device = input_devices_by_fd[fd]
        del input_devices_by_fd[fd]
        try:
            poll.unregister(input_device)
            input_device.close()
        except OSError:
            pass


class _KeyInfo(TypedDict):
    count: int


class _PressureInfo(TypedDict):
    name: str
    config: str
    keys: dict[str, _KeyInfo]


type _Pressures = dict[str | bytes, _PressureInfo]


def _handle_event(
    device: evdev.InputDevice[str],
    event: evdev.InputEvent,
    pressures: _Pressures,
    no_wait: bool,
    debug: bool,
    /,
) -> bool:
    if event.type == ecodes.EV_KEY:
        config_name = get_device_config_filename(device)
        if (code_name := ECODES_NAMES.get(event.code)) is not None:
            if debug:
                print(f'{device.path:<20} {code_name:<16} {device.name:<40} {config_name}', file=sys.stderr)

            device_pressures = pressures.setdefault(
                device.path, {'name': device.name, 'config': config_name, 'keys': {}}
            )
            key_info = device_pressures['keys'].setdefault(code_name, {'count': 0})

            key_info['count'] += 1

            if not no_wait:
                subprocess.run(['batocera-flash-screen', '0.1', '#ff00ff'])

            return True
    return False


def _do_output(pressures: _Pressures, ncount: int, evformat: bool, /) -> None:
    if not sys.stdout.isatty():
        print('<keys>')
    for evt, pressure in pressures.items():
        for key, key_info in pressure['keys'].items():
            if key_info['count'] == ncount:
                key_str = key

                if evformat:
                    key_str = _udev_to_ev_code(key)

                if sys.stdout.isatty():
                    print(f'{evt:<20} {key_str:<16} {pressure["name"]:<40} {pressure["config"]}')
                else:
                    print(
                        f'<key event="{evt}" key="{key_str}" config="{pressure["config"]}" count="{key_info["count"]}" />'
                    )
    if not sys.stdout.isatty():
        print('</keys>')


def _do_detect(
    ncount: int, duration: int, device_path: str | None, no_wait: bool, evformat: bool, debug: bool, /
) -> None:
    udev_context = pyudev.Context()
    poll = select.poll()
    input_devices_by_fd = _add_devices(poll, udev_context, device_path, debug)
    start_time = datetime.datetime.now()
    pressures: _Pressures = {}

    # read all devices
    if sys.stdout.isatty():
        print(f'Press {ncount} times buttons to filter', file=sys.stderr)

    try:
        found_one = False
        while datetime.datetime.now() - start_time < datetime.timedelta(seconds=duration) and (
            (no_wait and not found_one) or (not no_wait)
        ):
            try:
                for fd, _ in poll.poll(100):
                    try:
                        event = input_devices_by_fd[fd].read_one()
                        if (
                            event is not None
                            and event.type == ecodes.EV_KEY
                            and event.value == 1
                            and _handle_event(input_devices_by_fd[fd], event, pressures, no_wait, debug)
                        ):
                            found_one = True
                    except Exception as e:
                        # error on a single device
                        if (input_device := input_devices_by_fd.get(fd)) is not None:
                            if not (isinstance(e, OSError) and e.errno == errno.ENODEV):
                                print(e)
                                print(f'error on device {input_device.name} ({input_device.path}), closing.')

                            del input_devices_by_fd[fd]

                            try:
                                poll.unregister(input_device)
                                input_device.close()
                            except Exception:
                                pass
            except KeyboardInterrupt:
                # Swallow keyboard interrupt to allow graceful exit (cleanup runs in finally)
                return

        _do_output(pressures, ncount, evformat)
    finally:
        _remove_devices(poll, input_devices_by_fd)


def _get_config_fancy_name(file: Path, /) -> str:
    # remove the vip/pid, extension and replace _ by spaces
    x = re.sub(r'-[^-]*-[^-]*\.mapping', '', file.name.replace('_', ' '))
    # replace multiple spaces by single ones
    x = re.sub('[ ]+', ' ', x)
    return x.strip()


class _ConfigFileInfo(TypedDict):
    path: Path
    source: Literal['system', 'user']


def _get_all_config_files() -> dict[str, _ConfigFileInfo]:
    # Key by basename so a user mapping overrides a system one with the same name.
    configs: dict[str, _ConfigFileInfo] = {}

    for config_dir in (CONFIG_SYSTEMDIR, CONFIG_USERDIR):
        if not config_dir.exists():
            continue

        source = 'system' if config_dir == CONFIG_SYSTEMDIR else 'user'

        for file in config_dir.iterdir():
            if file.is_file() and file.suffix == '.mapping':
                configs[file.name] = {'path': file, 'source': source}

    return configs


def _get_configs_from_connected_devices() -> set[str]:
    res: set[str] = set()
    udev_context = pyudev.Context()
    for device in udev_context.list_devices(subsystem='input'):
        if device.device_node is not None and device.device_node.startswith('/dev/input/event'):
            dev = evdev.InputDevice(device.device_node)
            res.add(get_device_config_filename(dev))
            dev.close()
    return res


# to avoid listing all systems hotkeys (like almost nobody want to see the steamdeck hotkeys)
# filter list to existing devices
def _do_list() -> None:
    required_configs = _get_configs_from_connected_devices()

    n = 0

    if not sys.stdout.isatty():
        print('<hotkeys>')

    configs = _get_all_config_files()

    for name, infos in configs.items():
        # remove system configs from not connected devices
        if infos['source'] == 'system' and name not in required_configs:
            continue

        values = json.loads(infos['path'].read_text())
        fancy_name = _get_config_fancy_name(infos['path'])

        if sys.stdout.isatty():
            if n != 0:
                print('')
            print(f'{fancy_name} ({infos["path"]})')
            for key, action in values.items():
                print(f'  {key:<16} {action:<16}')
        else:
            print(f'  <device fancy_name="{fancy_name}" config="{infos["path"]}">')
            for key, action in values.items():
                print(f'    <hotkey key="{key}" action="{action}" />')
            print('  </device>')

        n += 1

    if not sys.stdout.isatty():
        print('</hotkeys>')


def _do_set(config: str, key: str, action: str | None) -> None:
    if not config.endswith('.mapping'):
        print('invalid configuration file', file=sys.stderr)
        return

    userpath = CONFIG_USERDIR / config
    systempath = CONFIG_SYSTEMDIR / config
    values = {}

    # read the user file. if not, ready the system file (but always write in the user file)
    if userpath.is_file():
        values = json.loads(userpath.read_text())
    elif systempath.is_file():
        values = json.loads(systempath.read_text())

    if action == 'none':
        values[key] = ''
    elif action is None:
        if key in values:
            del values[key]
    else:
        values[key] = action

    CONFIG_USERDIR.mkdir(parents=True, exist_ok=True)

    userpath.write_text(json.dumps(values, indent=4))


def _udev_to_ev_code(code: str, /) -> str:
    if code.startswith(('KEY_', 'BTN_', 'ABS_')):
        return f'{code[0:3]}:{code[4:]}'.lower()
    return code


class _HotkeyMapping(TypedDict):
    by_keys: dict[str, str]
    by_names: dict[str, str]


def _list_values(hotkeys_mapping: _HotkeyMapping) -> None:
    print('<mapping>')

    for key, value in sorted(hotkeys_mapping['by_names'].items()):
        evvalue = _udev_to_ev_code(value)
        print(f'<key code="{value}" evcode="{evvalue}" name="{key}" />')

    print('</mapping>')


def _read_hotkey_mapping(hotkey_mapping_file: Path) -> _HotkeyMapping:
    by_keys: dict[str, str] = json.loads(hotkey_mapping_file.read_text())
    by_names: dict[str, str] = {name: key for key, name in by_keys.items()}
    return {'by_keys': by_keys, 'by_names': by_names}


def main() -> None:
    parser = argparse.ArgumentParser(prog='batocera-hotkeys')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--count', type=int, help='detection count')
    parser.add_argument('--duration', type=int, help='detection duration (in seconds)')
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

    if args.detect:
        _do_detect(args.count or 2, args.duration or 4, args.device, args.nowait, args.evformat, args.debug)
    elif args.values:
        hotkeys_mapping = _read_hotkey_mapping(HOTKEYGEN_MAPPING)
        _list_values(hotkeys_mapping)
    elif args.remove:
        if args.config and args.key:
            _do_set(args.config, args.key, None)
            subprocess.run(['hotkeygen', '--reload'])  # reload the configuration
        else:
            parser.error('remove requires config and key arguments')
    elif args.set:
        if args.config and args.key and args.action:
            _do_set(args.config, args.key, args.action)
            subprocess.run(['hotkeygen', '--reload'])  # reload the configuration
        else:
            parser.error('set requires config, key and action arguments')
    else:
        _do_list()


if __name__ == '__main__':
    main()
