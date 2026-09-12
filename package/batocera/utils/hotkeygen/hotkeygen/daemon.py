from __future__ import annotations

import asyncio
import errno
import json
import os
import signal
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final, TypedDict

import evdev
import pyudev
import uvloop
from evdev import ecodes

from .shared import (
    CONFIG_DEFAULTDIR,
    CONFIG_SYSTEMDIR,
    CONFIG_USERDIR,
    DEVICE_NAME,
    ECODES_NAMES,
    HOTKEYGEN_MAPPING,
    get_device_config_filename,
    get_input_device,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    class HotkeysContext(TypedDict):
        name: str
        keys: dict[str, list[int] | int | str]

    class JsonHotkeysContext(TypedDict):
        name: str
        keys: dict[str, list[str] | str]


_DEFAULT_CONTEXT_FILE: Final = CONFIG_DEFAULTDIR / 'default_context.conf'
_COMMON_CONTEXT_FILE: Final = CONFIG_DEFAULTDIR / 'common_context.conf'

_CONTEXT_FILE: Final = Path('/var/run/hotkeygen.context')
_PID_FILE: Final = Path('/var/run/hotkeygen.pid')

_USER_COMMON_CONTEXT_FILE: Final = CONFIG_USERDIR / 'common_context.conf'
_USER_DEFAULT_MAPPING_FILE: Final = CONFIG_USERDIR / 'default_mapping.conf'

_g_debug = False


# default context is for es
def _get_default_context() -> HotkeysContext:
    if _DEFAULT_CONTEXT_FILE.exists():
        data = json.loads(_DEFAULT_CONTEXT_FILE.read_text())
        return _load_context(data)

    return {'name': '', 'keys': {}}


def _get_common_context_keys() -> dict[str, list[int] | int | str]:
    keys = {}
    userkeys = {}

    if _COMMON_CONTEXT_FILE.exists():
        data = json.loads(_COMMON_CONTEXT_FILE.read_text())
        keys = _load_context_keys(data)

    if _USER_COMMON_CONTEXT_FILE.exists():
        data = json.loads(_USER_COMMON_CONTEXT_FILE.read_text())
        userkeys = _load_context_keys(data)

    return keys | userkeys


def _get_context() -> HotkeysContext | None:
    if _CONTEXT_FILE.exists():
        try:
            if _g_debug:
                print(f'using default context {_CONTEXT_FILE}')
            return _load_context(json.loads(_CONTEXT_FILE.read_text()))
        except Exception as e:
            print(f'fail to load context file : {e}')
            return None
    else:
        context = _get_default_context()
        context['keys'] |= _get_common_context_keys()
        if _g_debug:
            print('using default context')
            _print_context(context)
        return context


def _load_context_keys(keys: dict[str, list[str] | str]) -> dict[str, list[int] | int | str]:
    res: dict[str, list[int] | int | str] = {}
    for action, key_code_names in keys.items():
        if isinstance(key_code_names, list):
            codes: list[int] = []
            res[action] = codes
            for x in key_code_names:
                if x in ecodes.ecodes:
                    codes.append(ecodes.ecodes[x])
                else:
                    raise Exception(f'invalid key {x!r}')
        else:
            # string are key if starting by KEY_ else commands (maybe not the best choice, but simple)
            if key_code_names[:4] == 'KEY_':
                if key_code_names in ecodes.ecodes:
                    res[action] = ecodes.ecodes[key_code_names]
                else:
                    raise Exception(f'invalid key {key_code_names!r}')
            else:
                # command
                res[action] = key_code_names
    return res


def _load_context(data: JsonHotkeysContext) -> HotkeysContext:
    if 'name' not in data:
        raise Exception('no name section found')
    if 'keys' not in data:
        raise Exception('no keys section found')

    context: HotkeysContext = {'name': data['name'], 'keys': {}}
    context['keys'] = _load_context_keys(data['keys'])
    if _g_debug:
        _print_context(context)
    return context


def _save_context(context: HotkeysContext, gcontext_file: Path) -> None:
    save: JsonHotkeysContext = {'name': context['name'], 'keys': {}}
    for action, key_codes in context['keys'].items():
        if isinstance(key_codes, list):
            save['keys'][action] = [ECODES_NAMES[key] for key in key_codes]
        elif isinstance(key_codes, str):
            save['keys'][action] = key_codes
        else:
            save['keys'][action] = ECODES_NAMES[key_codes]

    gcontext_file.write_text(json.dumps(save, indent=2))


def _print_context(context: HotkeysContext) -> None:
    print(f'Context [{context["name"]}]:')
    for action, keys in context['keys'].items():
        if isinstance(keys, list):
            print(f'  {action:-<20}-> {[ECODES_NAMES[key] for key in keys]}')
        elif isinstance(keys, str):
            print(f'  {action:-<20}-> command [{keys}]')
        else:
            print(f'  {action:-<20}-> {ECODES_NAMES[keys]}')


def _get_mapping_full_path(device: evdev.InputDevice[str]) -> Path | None:
    fullpath = None
    fname = get_device_config_filename(device)
    if _g_debug:
        print(f'...looking for {CONFIG_USERDIR}/{fname}, {CONFIG_SYSTEMDIR}/{fname}')
    if (CONFIG_USERDIR / fname).exists():
        fullpath = CONFIG_USERDIR / fname
    elif (CONFIG_SYSTEMDIR / fname).exists():
        fullpath = CONFIG_SYSTEMDIR / fname
    return fullpath


def _get_mapping(device: evdev.InputDevice[str] | None) -> dict[int, str]:
    if device is None:
        fullpath = None
    else:
        fullpath = _get_mapping_full_path(device)

    if fullpath is not None:
        if _g_debug:
            print(f'using mapping {fullpath}')

        data = json.loads(fullpath.read_text())
        return _load_mapping(data)

    data: dict[str, str] = {}
    userdata: dict[str, str] = {}
    if HOTKEYGEN_MAPPING.exists():
        if _g_debug:
            print(f'use default mapping file {HOTKEYGEN_MAPPING}')
        data = json.loads(HOTKEYGEN_MAPPING.read_text())
    if _USER_DEFAULT_MAPPING_FILE.exists():
        if _g_debug:
            print(f'use user mapping file {_USER_DEFAULT_MAPPING_FILE}')
        userdata = json.loads(_USER_DEFAULT_MAPPING_FILE.read_text())

    return _load_mapping(data | userdata)


def _load_mapping(data: dict[str, str]) -> dict[int, str]:
    try:
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


def _get_mapping_associations(mapping: Mapping[int, str], caps: evdev._AbsInfoCapabilities) -> dict[int, str]:
    capskeys = set(caps[ecodes.EV_KEY])
    return {key: value for key, value in mapping.items() if key in capskeys}


def _print_mapping(
    mapping: Mapping[int, str], associations: Mapping[int, str], context: HotkeysContext | None = None
) -> None:
    for k in mapping:
        if k in associations:
            if context is None:
                print(f'  {ECODES_NAMES[k]:-<15}-> {associations[k]}')
            else:
                if associations[k] in context['keys']:
                    key_codes = context['keys'][associations[k]]
                    if isinstance(key_codes, list):
                        key_names = [ECODES_NAMES[x] for x in key_codes]
                        print(f'  {ECODES_NAMES[k]:-<15}-> {associations[k]:-<15}-> {key_names}')
                    elif isinstance(key_codes, str):
                        print(f'  {ECODES_NAMES[k]:-<15}-> {associations[k]:-<15}-> {key_codes}')
                    else:
                        print(f'  {ECODES_NAMES[k]:-<15}-> {associations[k]:-<15}-> {ECODES_NAMES[key_codes]}')
                else:
                    print(f'  {ECODES_NAMES[k]:-<15}-> {associations[k]:15}')


def _send_keys(target: evdev.UInput, keys: int | list[int], begin: bool) -> None:
    if begin:
        n = 1
    else:
        n = 0

    if isinstance(keys, list):
        for x in keys:
            if _g_debug:
                print(f'sending EV_KEY {x} {n}')
            target.write(ecodes.EV_KEY, x, n)
            target.syn()
    else:
        if _g_debug:
            print(f'sending EV_KEY {keys} {n}')
        target.write(ecodes.EV_KEY, keys, n)
        target.syn()


async def _do_send(key: str, delay: int | None) -> None:
    if _g_debug:
        if delay:
            print(f'Sending {key} with delay {delay}')
        else:
            print(f'Sending {key}')

    mapping = _get_mapping(None)
    for code in mapping:
        if mapping[code] == key:
            if _g_debug:
                print(f'sending {key}')

            sender = evdev.UInput(name='virtual keyboard', events={ecodes.EV_KEY: [code]})

            try:
                # need some time to initialize... (otherwise the first events are ignored the time add is taken)
                await asyncio.sleep(0.1)
                _send_keys(sender, code, True)

                # time required for emulators (like mame) based on states and not on events
                # (if you go too fast, the event is not seen)
                if delay:
                    await asyncio.sleep(delay)
                else:
                    # some emulators (ra, mame) needs some time otherwise they don't see the touch was pressed
                    await asyncio.sleep(0.3)

                _send_keys(sender, code, False)

            finally:
                sender.close()


async def _send_reset_signal(target_device: evdev.UInput, /) -> None:
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


async def _do_reset_mouse() -> None:
    # Create temporary device
    sender = evdev.UInput(
        name='batocera-mouse-reset',
        events={ecodes.EV_REL: [ecodes.REL_X, ecodes.REL_Y], ecodes.EV_KEY: [ecodes.BTN_LEFT]},
    )

    try:
        await asyncio.sleep(0.2)

        await _send_reset_signal(sender)
    finally:
        sender.close()


def _read_pid() -> str:
    return _PID_FILE.read_text().replace('\n', '')


def _do_new_context(
    context_name: str | None = None, context_json: str | None = None, include_common: bool = True
) -> None:
    if context_name is not None and context_json is not None:
        context = _load_context({'name': context_name, 'keys': json.loads(context_json)})
        if include_common:
            context['keys'] |= _get_common_context_keys()

        # update the config file
        _save_context(context, _CONTEXT_FILE)
    else:
        if _CONTEXT_FILE.exists():
            _CONTEXT_FILE.unlink()

    # inform the process
    pid = int(_read_pid())
    os.kill(pid, signal.SIGHUP)


def _do_reload_devices_config():
    # inform the process
    pid = int(_read_pid())
    os.kill(pid, signal.SIGHUP)


def _get_input_device_mapping(
    device: pyudev.Device, /
) -> tuple[evdev.InputDevice[str], dict[int, str], dict[int, str]] | None:
    if (input_device := get_input_device(device)) is not None:
        capabilities = input_device.capabilities()
        mapping = _get_mapping(input_device)
        return input_device, mapping, _get_mapping_associations(mapping, capabilities)

    return None


def _do_list() -> None:
    context = _get_context()

    udev_context = pyudev.Context()

    if context is not None:
        _print_context(context)

    for device in udev_context.list_devices(subsystem='input'):
        input_device_mapping = _get_input_device_mapping(device)

        if input_device_mapping is None:
            continue

        dev, mapping, associations = input_device_mapping

        try:
            if fullpath := _get_mapping_full_path(dev):
                print(f'# device {device.device_node} [{dev.name}] ({fullpath})')
            else:
                fname = get_device_config_filename(dev)
                print(f'# device {device.device_node} [{dev.name}] (no {fname} file found)')

            if associations:
                _print_mapping(mapping, associations, context)

        finally:
            dev.close()


def _check_device(func: Callable[[_Daemon, pyudev.Device], None]) -> Callable[[_Daemon, pyudev.Device], None]:
    def wrapper(self: _Daemon, device: pyudev.Device, /) -> None:
        if device.device_node is not None and device.device_node.startswith('/dev/input/event'):
            func(self, device)

    return wrapper


@dataclass(slots=True)
class _Daemon:
    permanent: bool = field(kw_only=True)

    context: HotkeysContext | None = field(init=False, default=None)
    running: bool = field(init=False, default=False)
    input_devices: dict[str | bytes, evdev.InputDevice[str]] = field(
        init=False, default_factory=dict[str | bytes, evdev.InputDevice[str]]
    )
    mappings: dict[str | bytes, dict[int, str]] = field(init=False, default_factory=dict[str | bytes, dict[int, str]])
    udev_context: pyudev.Context = field(init=False)
    monitor: pyudev.Monitor = field(init=False)
    target: evdev.UInput = field(init=False)
    device_tasks: dict[str | bytes, asyncio.Task[None]] = field(
        init=False, default_factory=dict[str | bytes, asyncio.Task[None]]
    )
    background_tasks: set[asyncio.Task[int]] = field(init=False, default_factory=set[asyncio.Task[int]])

    def __post_init__(self) -> None:
        self.udev_context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.udev_context)
        self.monitor.filter_by(subsystem='input')

        keys_list = [x for x in range(ecodes.KEY_MAX) if x in ECODES_NAMES and ECODES_NAMES[x][:4] == 'KEY_']
        keys_list.append(ecodes.BTN_LEFT)

        # target virtual keyboard & mouse
        self.target = evdev.UInput(
            name=DEVICE_NAME, events={ecodes.EV_KEY: keys_list, ecodes.EV_REL: [ecodes.REL_X, ecodes.REL_Y]}
        )

    async def __device_loop(self, device: evdev.InputDevice[str], /) -> None:
        path = device.path

        try:
            async for event in device.async_read_loop():
                if event.type != ecodes.EV_KEY:
                    continue

                mapping = self.mappings.get(path)
                if mapping is None or event.code not in mapping:
                    continue
                action = mapping[event.code]
                if event.value == 1:
                    await self.__handle_event(event, action, True)
                elif event.value == 0:
                    await self.__handle_event(event, action, False)
        except asyncio.CancelledError:
            raise
        except OSError as e:
            if e.errno != errno.ENODEV:
                print(e)
                print(f'error on device {device.name} ({path}), closing.')
        finally:
            self.mappings.pop(path, None)
            self.input_devices.pop(path, None)
            self.device_tasks.pop(path, None)
            try:
                device.close()
            except OSError:
                pass

    async def __handle_event(self, event: evdev.InputEvent, action: str, begin: bool) -> None:
        if self.context is not None and action in self.context['keys']:
            keys = self.context['keys'][action]

            if action == 'exit' and ((isinstance(keys, str) and not begin) or (not isinstance(keys, str) and begin)):
                await _send_reset_signal(self.target)

            if _g_debug:
                print(f'code:{event.code}, value:{event.value}, action:{action}')

            if begin:
                if isinstance(keys, str):
                    pass  # nothing on keydown
                else:
                    _send_keys(self.target, keys, True)
            else:
                if isinstance(keys, str):
                    proc = await asyncio.create_subprocess_shell(keys)
                    task = asyncio.create_task(proc.wait())
                    self.background_tasks.add(task)
                    task.add_done_callback(self.background_tasks.discard)
                else:
                    _send_keys(self.target, keys, False)

    def __reload_devices_configs(self) -> None:
        # reload config files for devices
        for path, input_device in self.input_devices.items():
            self.mappings[path] = _get_mapping(input_device)

        # try to load a device that had not configuration file before
        for device in self.udev_context.list_devices(subsystem='input'):
            self.__handle_udev_add(device)

    @_check_device
    def __handle_udev_add(self, device: pyudev.Device, /) -> None:
        assert device.device_node is not None

        if device.device_node in self.device_tasks:
            return

        input_device_mapping = _get_input_device_mapping(device)

        if input_device_mapping is None:
            return

        input_device, mapping, associations = input_device_mapping
        path = device.device_node
        watched = False

        try:
            if associations:
                if _g_debug:
                    print(f'Adding device {path}: {input_device.name}')
                    _print_mapping(mapping, associations)

                self.input_devices[path] = input_device
                self.mappings[path] = mapping
                self.device_tasks[path] = asyncio.create_task(
                    self.__device_loop(input_device),
                    name=f'evdev:{path}',
                )
                watched = True
        finally:
            if not watched:
                input_device.close()

    @_check_device
    def __handle_udev_remove(self, device: pyudev.Device, /) -> None:
        assert device.device_node is not None

        path = device.device_node
        task = self.device_tasks.get(path)

        if task is not None:
            if _g_debug:
                input_device = self.input_devices.get(path)
                name = input_device.name if input_device is not None else '?'
                print(f'Removing device {path}: {name}')
            task.cancel()

    def __on_udev(self) -> None:
        try:
            # Drain the queue; add_reader only guarantees ≥1 event.
            while (device := self.monitor.poll(0)) is not None:
                match device.action:
                    case 'add':
                        self.__handle_udev_add(device)
                    case 'remove':
                        self.__handle_udev_remove(device)
                    case _:
                        pass
        except Exception as e:
            print('Exception happened on the monitor fd')
            print(e)

    def __on_sighup(self) -> None:
        self.context = _get_context()
        self.__reload_devices_configs()

    async def run(self) -> None:
        if self.running:
            raise Exception('already running!')

        self.running = True
        self.context = _get_context()

        # permanent : write a pid so that new configuration can apply
        if self.permanent:
            _PID_FILE.write_text(str(os.getpid()))

        # monitor all udev devices
        self.monitor.start()
        loop = asyncio.get_running_loop()
        loop.add_reader(self.monitor, self.__on_udev)

        # to read new contexts
        loop.add_signal_handler(signal.SIGHUP, self.__on_sighup)

        # adding existing devices
        for device in self.udev_context.list_devices(subsystem='input'):
            self.__handle_udev_add(device)

        try:
            await asyncio.Event().wait()  # wait forever
        finally:
            loop.remove_reader(self.monitor)

            for task in self.background_tasks:
                task.cancel()

            for task in self.device_tasks.values():
                task.cancel()

            await asyncio.gather(*self.background_tasks, *self.device_tasks.values(), return_exceptions=True)

            self.target.close()


async def _run(args: Namespace, /) -> None:
    global _g_debug

    if args.debug:
        _g_debug = True

    if args.list:
        _do_list()
    elif args.reset_mouse:
        await _do_reset_mouse()
    elif args.send is not None:
        await _do_send(args.send, args.send_delay)
    elif args.new_context is not None:
        new_context_name, new_context_json = args.new_context
        _do_new_context(new_context_name, new_context_json, not args.disable_common)
    elif args.reload:
        _do_reload_devices_config()
    elif args.default_context:
        _do_new_context()
    else:
        await _Daemon(permanent=args.permanent).run()


def main() -> None:
    global _g_debug

    parser = ArgumentParser(prog='hotkeygen')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--send')
    parser.add_argument('--send-delay', type=int)
    parser.add_argument('--default-context', action='store_true')
    parser.add_argument('--new-context', nargs=2, metavar=('new-context-name', 'new-context-json'))
    parser.add_argument('--disable-common', action='store_true')
    parser.add_argument('--reload', action='store_true')
    parser.add_argument('--permanent', action='store_true')
    parser.add_argument('--reset-mouse', action='store_true')

    args = parser.parse_args()

    uvloop.run(_run(args))


if __name__ == '__main__':
    main()
