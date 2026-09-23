from __future__ import annotations

import asyncio
import errno
import json
import os
import signal
from copy import deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final

import evdev
import pyudev
from evdev import ecodes

from batocera_common.fs import atomic_write
from batocera_common.paths import existing_files_in_directories, glob_in_directories

from .dbus.service import Service
from .paths import (
    CONFIG_DEFAULTDIR,
    CONFIG_SYSTEMDIR,
    CONFIG_USERDIR,
    CONTEXT_FILE,
    DEVICE_NAME,
    PID_FILE,
    SYSTEM_DEFAULT_MAPPING,
)
from .utils import (
    get_device_config_filename,
    get_device_mapping,
    get_device_mapping_path,
    get_hotkeys_context,
    get_input_device,
    print_mapping,
    reset_device,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Mapping
    from pathlib import Path

    from ._types import HotkeysContext, HotkeysContextMapping, PersistedHotkeysContext


_DEFAULT_CONTEXT_FILE: Final = CONFIG_DEFAULTDIR / 'default_context.conf'


# default context is for ES
def _load_default_context() -> HotkeysContextMapping:
    context: HotkeysContextMapping | None = None

    if _DEFAULT_CONTEXT_FILE.exists():
        try:
            context = json.loads(_DEFAULT_CONTEXT_FILE.read_text())
        except Exception as e:
            print(f'failed to load default context file : {e}')

    if context is None:
        context = {'name': '', 'keys': {}}

    return context


def _load_initial_context(debug: bool) -> HotkeysContext:
    context: HotkeysContextMapping | None = None
    include_common = True

    if CONTEXT_FILE.exists():
        try:
            persisted: PersistedHotkeysContext = json.loads(CONTEXT_FILE.read_text())

            context = persisted.get('context')
            include_common = persisted.get('include_common', True)
        except Exception as e:
            print(f'failed to load persisted context file : {e}')

    if context is None:
        context = _load_default_context()
        include_common = True

    return get_hotkeys_context(context, include_common, debug=debug)


def _get_mapping_associations(mapping: Mapping[int, str], caps: evdev._AbsInfoCapabilities) -> dict[int, str]:
    capskeys = set(caps[ecodes.EV_KEY])
    return {key: value for key, value in mapping.items() if key in capskeys}


def _send_keys(target: evdev.UInput, keys: int | list[int], begin: bool, debug: bool) -> None:
    if begin:
        n = 1
    else:
        n = 0

    if isinstance(keys, list):
        for x in keys:
            if debug:
                print(f'sending EV_KEY {x} {n}')
            target.write(ecodes.EV_KEY, x, n)
            target.syn()
    else:
        if debug:
            print(f'sending EV_KEY {keys} {n}')
        target.write(ecodes.EV_KEY, keys, n)
        target.syn()


def _get_input_device_mapping(
    device: pyudev.Device, debug: bool, /
) -> tuple[evdev.InputDevice[str], dict[int, str], dict[int, str]] | None:
    if (input_device := get_input_device(device)) is not None:
        capabilities = input_device.capabilities()
        mapping = get_device_mapping(input_device, debug)
        return input_device, mapping, _get_mapping_associations(mapping, capabilities)

    return None


def _check_device(func: Callable[[Daemon, pyudev.Device], None]) -> Callable[[Daemon, pyudev.Device], None]:
    def wrapper(self: Daemon, device: pyudev.Device, /) -> None:
        if device.device_node is not None and device.device_node.startswith('/dev/input/event'):
            func(self, device)

    return wrapper


@dataclass(slots=True)
class Daemon:
    debug: bool = field(kw_only=True)
    permanent: bool = field(kw_only=True)

    context: HotkeysContext = field(init=False)
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

        self.context = _load_initial_context(self.debug)

        keys_list = [code for code, name in evdev.ecodes.KEY.items() if name != 'KEY_MAX' and name != 'KEY_CNT']
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

                if (mapping := self.mappings.get(path)) is None or (action := mapping.get(event.code)) is None:
                    continue

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
        if (keys := self.context['keys'].get(action)) is not None:
            if action == 'exit' and ((isinstance(keys, str) and not begin) or (not isinstance(keys, str) and begin)):
                await reset_device(self.target)

            if self.debug:
                print(f'code:{event.code}, value:{event.value}, action:{action}')

            if begin:
                if isinstance(keys, str):
                    pass  # nothing on keydown
                else:
                    _send_keys(self.target, keys, True, self.debug)
            else:
                if isinstance(keys, str):
                    proc = await asyncio.create_subprocess_shell(keys)
                    task = asyncio.create_task(proc.wait())
                    self.background_tasks.add(task)
                    task.add_done_callback(self.background_tasks.discard)
                else:
                    _send_keys(self.target, keys, False, self.debug)

    @_check_device
    def __handle_udev_add(self, device: pyudev.Device, /) -> None:
        assert device.device_node is not None

        if device.device_node in self.device_tasks:
            return

        input_device_mapping = _get_input_device_mapping(device, self.debug)

        if input_device_mapping is None:
            return

        input_device, mapping, associations = input_device_mapping
        path = device.device_node
        watched = False

        try:
            if associations:
                if self.debug:
                    print(f'Adding device {path}: {input_device.name}')
                    print_mapping(mapping, associations)

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
            if self.debug:
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

    def __set_context(self, context: HotkeysContextMapping | None, /, include_common: bool = True) -> None:
        persist_context = context is not None

        if context is None:
            try:
                CONTEXT_FILE.unlink(missing_ok=True)
            except Exception as e:
                print(f'failed to remove persisted context: {e}')

            context = _load_default_context()

        self.context = get_hotkeys_context(context, include_common, debug=self.debug)

        if persist_context:
            try:
                with atomic_write(CONTEXT_FILE) as context_file:
                    context_file.write_text(
                        json.dumps(
                            {
                                'context': context,
                                'include_common': include_common,
                            },
                            indent=4,
                        )
                    )
            except Exception as e:
                print(f'failed to persist context: {e}')

        self.__reload_device_mappings()

    def __reload_device_mappings(self) -> None:
        # reload config files for devices
        for path, input_device in self.input_devices.items():
            self.mappings[path] = get_device_mapping(input_device, self.debug)

        # try to load a device that had not configuration file before
        for device in self.udev_context.list_devices(subsystem='input'):
            self.__handle_udev_add(device)

    ## begin ContextBackend

    def set_context(self, context: HotkeysContextMapping, /, include_common: bool = True) -> None:
        self.__set_context(context, include_common=include_common)

    def set_default_context(self) -> None:
        self.__set_context(None, include_common=True)

    def get_context(self) -> HotkeysContext:
        return deepcopy(self.context)

    def get_device_mappings(self) -> dict[tuple[str, str, str, str], tuple[dict[int, str], dict[int, str]]]:
        return {
            (
                device.path,
                device.name,
                get_device_config_filename(device),
                str(get_device_mapping_path(device, False) or ''),
            ): (
                mapping,
                _get_mapping_associations(mapping, device.capabilities()),
            )
            for path, device in self.input_devices.items()
            if (mapping := self.mappings.get(path)) is not None
        }

    def reload(self) -> None:
        if not self.context['name']:
            self.set_default_context()
        else:
            self.__reload_device_mappings()

    ## end ContextBackend

    ## begin HotkeyBackend

    async def send_hotkey(self, key: str, delay: int | None, /) -> None:
        if self.debug:
            if delay:
                print(f'Sending {key} with delay {delay}')
            else:
                print(f'Sending {key}')

        mapping = get_device_mapping(None, self.debug)
        for code in mapping:
            if mapping[code] == key:
                if self.debug:
                    print(f'sending {key}')

                sender = evdev.UInput(name='virtual keyboard', events={ecodes.EV_KEY: [code]})

                try:
                    # need some time to initialize... (otherwise the first events are ignored the time add is taken)
                    await asyncio.sleep(0.1)
                    _send_keys(sender, code, True, self.debug)

                    # time required for emulators (like mame) based on states and not on events
                    # (if you go too fast, the event is not seen)
                    if delay:
                        await asyncio.sleep(delay)
                    else:
                        # some emulators (ra, mame) needs some time otherwise they don't see the touch was pressed
                        await asyncio.sleep(0.3)

                    _send_keys(sender, code, False, self.debug)

                finally:
                    sender.close()

    ## end HotkeyBackend

    ## begin ConfigBackend

    def get_system_default_mapping_config(self) -> tuple[dict[str, str], dict[str, str]]:
        by_keys: dict[str, str] = json.loads(SYSTEM_DEFAULT_MAPPING.read_text())
        by_names: dict[str, str] = {name: key for key, name in by_keys.items()}

        return by_keys, by_names

    def __get_connected_input_devices(self) -> Iterator[evdev.InputDevice[str]]:
        for udev_device in self.udev_context.list_devices(subsystem='input'):
            if udev_device.device_node is not None and udev_device.device_node.startswith('/dev/input/event'):
                input_device = evdev.InputDevice(udev_device.device_node)

                try:
                    yield input_device
                finally:
                    input_device.close()

    def __get_connected_mapping_files(self) -> Iterator[Path]:
        connected_mapping_filenames = {
            get_device_config_filename(device) for device in self.__get_connected_input_devices()
        }

        seen_user_mappings = set[str]()

        for file in glob_in_directories('*.mapping', (CONFIG_USERDIR, CONFIG_SYSTEMDIR)):
            if not file.is_file():
                continue

            if file.is_relative_to(CONFIG_SYSTEMDIR) and (
                file.name in seen_user_mappings or file.name not in connected_mapping_filenames
            ):
                continue
            else:
                seen_user_mappings.add(file.name)

            yield file

    def get_device_mapping_config(self) -> dict[str, dict[str, str]]:
        device_mappings: dict[str, dict[str, str]] = {}

        for mapping_file in self.__get_connected_mapping_files():
            try:
                values = json.loads(mapping_file.read_text())
            except Exception as e:
                print(f'error while reading mapping file "{mapping_file}": {e}')
                continue

            device_mappings[mapping_file.name] = values

        return device_mappings

    def __write_device_mapping_config(self, filename: str, key: str, action: str | None, /) -> None:
        if not filename.endswith('.mapping'):
            raise ValueError(f'filename must end with .mapping, got {filename!r}')

        user_file = CONFIG_USERDIR / filename

        values: dict[str, str] = {}

        # read the user file. if not, read the system file (but always write in the user file)
        for path in existing_files_in_directories(filename, (CONFIG_USERDIR, CONFIG_SYSTEMDIR)):
            values = json.loads(path.read_text())
            break

        if action is None:
            values.pop(key, None)
        else:
            values[key] = '' if action == 'none' else action

        user_file.parent.mkdir(parents=True, exist_ok=True)

        with atomic_write(user_file) as user_file:
            user_file.write_text(json.dumps(values, indent=4))

    def set_device_mapping_config(self, filename: str, key: str, action: str, /) -> None:
        self.__write_device_mapping_config(filename, key, action)
        self.__reload_device_mappings()

    def remove_device_mapping_config(self, filename: str, key: str, /) -> None:
        self.__write_device_mapping_config(filename, key, None)
        self.__reload_device_mappings()

    ## end ConfigBackend

    async def run(self) -> None:
        if self.running:
            raise Exception('already running!')

        self.running = True

        # permanent : write a pid so that new configuration can apply
        if self.permanent:
            PID_FILE.write_text(str(os.getpid()))

        # monitor all udev devices
        self.monitor.start()
        loop = asyncio.get_running_loop()
        loop.add_reader(self.monitor, self.__on_udev)

        # to read new contexts
        loop.add_signal_handler(signal.SIGHUP, self.reload)

        # adding existing devices
        for device in self.udev_context.list_devices(subsystem='input'):
            self.__handle_udev_add(device)

        try:
            async with Service(self):
                await asyncio.Event().wait()  # wait forever
        finally:
            loop.remove_reader(self.monitor)

            for task in self.background_tasks:
                task.cancel()

            for task in self.device_tasks.values():
                task.cancel()

            await asyncio.gather(*self.background_tasks, *self.device_tasks.values(), return_exceptions=True)

            self.target.close()
