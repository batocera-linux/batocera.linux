from __future__ import annotations

import argparse
import asyncio
import errno
import re
import subprocess
import sys
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from collections.abc import Iterator

    import evdev
    import pyudev

    from .dbus.client import Client


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
    config_name: str,
    debug: bool,
    /,
) -> int:
    from evdev import ecodes

    from .utils import get_ecode_name

    if event.type == ecodes.EV_KEY and event.value == 1:
        try:
            code_name = get_ecode_name(event.code)

            if debug:
                print(f'{device.path:<20} {code_name:<16} {device.name:<40} {config_name}', file=sys.stderr)

            if device.path not in pressures:
                device_pressures = pressures[device.path] = {'name': device.name, 'config': config_name, 'keys': {}}
            else:
                device_pressures = pressures[device.path]

            if code_name not in device_pressures['keys']:
                key_info = device_pressures['keys'][code_name] = {'count': 0}
            else:
                key_info = device_pressures['keys'][code_name]

            key_info['count'] += 1

            return True

        except KeyError:
            pass

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


async def _device_loop(
    device: evdev.InputDevice[str],
    pressures: _Pressures,
    found_one: asyncio.Event | None,
    debug: bool,
    /,
) -> None:
    from .utils import get_device_config_filename

    config_name = get_device_config_filename(device)

    try:
        async for event in device.async_read_loop():
            if _handle_event(device, event, pressures, config_name, debug):
                if found_one is not None:
                    found_one.set()
                else:
                    subprocess.run(['batocera-flash-screen', '0.1', '#ff00ff'])

    except Exception as e:
        if not (isinstance(e, OSError) and e.errno == errno.ENODEV):
            print(e)
            print(f'error on device {device.name} ({device.path}), closing.')


def _iterate_input_devices(
    udev_context: pyudev.Context, device_path: str | None, /
) -> Iterator[evdev.InputDevice[str]]:
    from .utils import get_input_device

    for device in udev_context.list_devices(subsystem='input'):
        if (device_path is None or device_path == device.device_node) and (
            input_device := get_input_device(device)
        ) is not None:
            yield input_device


async def _do_detect(
    start_count: int,
    duration: int,
    device_path: str | None,
    no_wait: bool,
    evformat: bool,
    debug: bool,
    /,
) -> None:
    import pyudev

    udev_context = pyudev.Context()

    # read all devices
    if sys.stdout.isatty():
        print(f'Press {start_count} times buttons to filter', file=sys.stderr)

    input_devices: list[evdev.InputDevice[str]] = []
    device_tasks: list[asyncio.Task[None]] = []
    pressures: _Pressures = {}
    found_one = asyncio.Event() if no_wait else None

    try:
        for input_device in _iterate_input_devices(udev_context, device_path):
            if debug:
                print(f'listening device {input_device.path:<18} {input_device.name}', file=sys.stderr)

            input_devices.append(input_device)
            device_tasks.append(
                asyncio.create_task(
                    _device_loop(input_device, pressures, found_one, debug),
                    name=f'detect:{input_device.path}',
                )
            )

        try:
            if found_one is None:
                # --nowait was not passed, so we wait for the duration to finish
                await asyncio.sleep(duration)
            else:
                # --nowait was passed, so we wait for the duration OR until a key
                # is pressed on any device (`found_one` is set)
                async with asyncio.timeout(duration):
                    await found_one.wait()
        except Exception:
            pass

        _do_output(pressures, start_count, evformat)
    finally:
        for task in device_tasks:
            try:
                task.cancel()
            except Exception:
                pass

        await asyncio.gather(*device_tasks, return_exceptions=True)

        for device in input_devices:
            try:
                device.close()
            except Exception:
                pass


def _get_config_fancy_name(file: str, /) -> str:
    # remove the vip/pid, extension and replace _ by spaces
    x = re.sub(r'-[^-]*-[^-]*\.mapping', '', file.replace('_', ' '))
    # replace multiple spaces by single ones
    x = re.sub('[ ]+', ' ', x)
    return x.strip()


# to avoid listing all systems hotkeys (like almost nobody want to see the steamdeck hotkeys)
# filter list to existing devices
async def _do_list(client: Client, /) -> None:
    if not sys.stdout.isatty():
        print('<hotkeys>')

    for n, (filename, mapping) in enumerate((await client.get_device_mapping_config()).items()):
        fancy_name = _get_config_fancy_name(filename)

        if sys.stdout.isatty():
            if n != 0:
                print('')
            print(f'{fancy_name} ({filename})')
            for key, action in mapping.items():
                print(f'  {key:<16} {action:<16}')
        else:
            print(f'  <device fancy_name="{fancy_name}" config="{filename}">')
            for key, action in mapping.items():
                print(f'    <hotkey key="{key}" action="{action}" />')
            print('  </device>')

    if not sys.stdout.isatty():
        print('</hotkeys>')


def _udev_to_ev_code(code: str, /) -> str:
    if code.startswith(('KEY_', 'BTN_', 'ABS_')):
        return f'{code[0:3]}:{code[4:]}'.lower()
    return code


async def _list_values(client: Client, /) -> None:
    _, by_names = await client.get_system_default_mapping_config()

    print('<mapping>')

    for key, value in sorted(by_names.items()):
        evvalue = _udev_to_ev_code(value)
        print(f'<key code="{value}" evcode="{evvalue}" name="{key}" />')

    print('</mapping>')


async def _do_dbus_actions(args: argparse.Namespace, /) -> None:
    from .dbus.client import Client

    async with Client() as client:
        if args.values:
            await _list_values(client)
        elif args.remove:
            await client.remove_device_mapping_config(args.config, args.key)
        elif args.set:
            await client.set_device_mapping_config(args.config, args.key, args.action)
        else:
            await _do_list(client)


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

    if not args.detect and not args.values:
        if args.remove and (not args.config or not args.key):
            parser.error('remove requires config and key arguments')
        elif args.set and (not args.config or not args.key or not args.action):
            parser.error('set requires config, key and action arguments')

    try:
        import uvloop

        if args.detect:
            uvloop.run(
                _do_detect(args.count or 2, args.duration or 4, args.device, args.nowait, args.evformat, args.debug)
            )
        else:
            uvloop.run(_do_dbus_actions(args))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
