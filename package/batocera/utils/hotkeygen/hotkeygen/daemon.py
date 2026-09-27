from __future__ import annotations

import asyncio
import errno
import json
import os
import signal
from copy import deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final, Self

import evdev
import pyudev
from evdev import ecodes

from batocera_common.asyncio import cancel_all, iterate_queue
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
    reset_pointer_position,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterator, Mapping
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


def _should_ignore_device(device: pyudev.Device, /) -> bool:
    return device.device_node is None or not device.device_node.startswith('/dev/input/event')


@dataclass(slots=True)
class HotkeyActivation:
    _finish: Callable[[], Awaitable[None]]
    _cancel: Callable[[], Awaitable[None]]
    _completed: bool = field(init=False, default=False)

    async def finish(self) -> None:
        if self._completed:
            return

        self._completed = True
        await self._finish()

    async def cancel(self) -> None:
        if self._completed:
            return

        self._completed = True
        await self._cancel()


@dataclass(slots=True)
class DeviceLoop:
    device: evdev.InputDevice[str]
    mappings: dict[int, str]
    begin_hotkey: Callable[[str], Awaitable[HotkeyActivation | None]]
    debug: bool = field(kw_only=True)

    task: asyncio.Task[None] | None = field(init=False, default=None)
    active_hotkeys: dict[int, HotkeyActivation] = field(init=False, default_factory=dict[int, HotkeyActivation])

    @property
    def path(self) -> str:
        return self.device.path

    def reload_mappings(self) -> None:
        self.mappings = get_device_mapping(self.device, self.debug)

    async def read_loop(self) -> None:
        path = self.device.path

        try:
            async for event in self.device.async_read_loop():
                if self.task is None:
                    break

                if event.type != ecodes.EV_KEY:
                    continue

                if event.value == 0:
                    if activation := self.active_hotkeys.pop(event.code, None):
                        await activation.finish()
                    continue

                if event.value != 1:
                    continue

                if (action := self.mappings.get(event.code)) is None:
                    continue

                # Defensive handling for an unexpected second keydown.
                if previous := self.active_hotkeys.pop(event.code, None):
                    await previous.cancel()

                if activation := await self.begin_hotkey(action):
                    self.active_hotkeys[event.code] = activation

        except OSError as e:
            if e.errno != errno.ENODEV:
                print(e)
                print(f'error on device {self.device.name} ({path}), closing.')
        finally:
            activations = list(self.active_hotkeys.values())
            self.active_hotkeys.clear()

            await asyncio.gather(
                *(activation.cancel() for activation in activations),
                return_exceptions=True,
            )

    def get_device_mapping_item(self) -> tuple[tuple[str, str, str, str], tuple[dict[int, str], dict[int, str]]]:
        return (
            self.device.path,
            self.device.name,
            get_device_config_filename(self.device),
            str(get_device_mapping_path(self.device, False) or ''),
        ), (
            self.mappings,
            _get_mapping_associations(self.mappings, self.device.capabilities()),
        )

    def close_device(self) -> None:
        try:
            self.device.close()
        except OSError:
            pass

    def start(self, on_complete: Callable[[Self], None]) -> Self:
        if self.task is not None:
            raise RuntimeError('DeviceLoop already started')

        self.task = asyncio.create_task(self.read_loop(), name=f'evdev:{self.device.path}')

        # Always close the device when the task is done. Done callbacks always run, even if
        # the task was cancelled before it started executing, so this ensures the device is
        # closed in all cases.
        self.task.add_done_callback(lambda _: self.close_device())
        self.task.add_done_callback(lambda _: on_complete(self))

        return self

    async def stop(self) -> None:
        if self.task is None:
            return

        loop_task = self.task

        # Set this to None so that if stop() is called again while waiting for the task to
        # finish, it doesn't try to cancel it again.
        self.task = None

        loop_task.cancel()
        await asyncio.gather(loop_task, return_exceptions=True)


@dataclass(slots=True)
class Daemon:
    debug: bool = field(kw_only=True)
    permanent: bool = field(kw_only=True)

    context: HotkeysContext = field(init=False)
    running: bool = field(init=False, default=False)
    stopping: bool = field(init=False, default=False)
    device_loops: dict[str | bytes, DeviceLoop] = field(init=False, default_factory=dict[str | bytes, DeviceLoop])
    background_tasks: set[asyncio.Task[int]] = field(init=False, default_factory=set[asyncio.Task[int]])
    tracked_backend_tasks: set[asyncio.Task[None]] = field(init=False, default_factory=set[asyncio.Task[None]])

    udev_context: pyudev.Context = field(init=False, default_factory=pyudev.Context)
    monitor: pyudev.Monitor = field(init=False)
    target: evdev.UInput = field(init=False)

    udev_events: asyncio.Queue[pyudev.Device] = field(init=False, default_factory=asyncio.Queue[pyudev.Device])
    udev_task: asyncio.Task[None] = field(init=False)

    def __post_init__(self) -> None:
        self.monitor = pyudev.Monitor.from_netlink(self.udev_context)
        self.monitor.filter_by(subsystem='input')

        self.context = _load_initial_context(self.debug)

        keys_list = [code for code, name in evdev.ecodes.KEY.items() if name != 'KEY_MAX' and name != 'KEY_CNT']
        keys_list.append(ecodes.BTN_LEFT)

        # target virtual keyboard & mouse
        self.target = evdev.UInput(
            name=DEVICE_NAME, events={ecodes.EV_KEY: keys_list, ecodes.EV_REL: [ecodes.REL_X, ecodes.REL_Y]}
        )

    def __on_device_loop_complete(self, loop: DeviceLoop, /) -> None:
        # If the loop was removed from the dict, it means it was already stopped and removed
        # by a udev remove event, so we don't need to remove it again.
        if self.device_loops.get(loop.path) is loop:
            self.device_loops.pop(loop.path, None)

    def __add_udev_device(self, device: pyudev.Device, /) -> None:
        if _should_ignore_device(device):
            return

        assert device.device_node is not None

        if device.device_node in self.device_loops:
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

                self.device_loops[path] = DeviceLoop(
                    input_device,
                    mapping,
                    self.__begin_hotkey,
                    debug=self.debug,
                ).start(self.__on_device_loop_complete)

                watched = True
        finally:
            if not watched:
                input_device.close()

    async def __handle_udev_add(self, device: pyudev.Device, /) -> None:
        assert device.device_node is not None

        # If udev reports the same path again, remove the old loop and then
        # stop it. Stopping the loop will try will close the device. Removing
        # the old loop from the dict ensures that a new loop can be added when
        # __add_udev_device is called below.
        if (loop := self.device_loops.pop(device.device_node, None)) is not None:
            await loop.stop()

        self.__add_udev_device(device)

    async def __handle_udev_remove(self, device: pyudev.Device, /) -> None:
        assert device.device_node is not None

        if (loop := self.device_loops.pop(device.device_node, None)) is None:
            return

        if self.debug:
            print(f'Removing device {device.device_node}: {loop.device.name}')

        await loop.stop()

    async def __udev_loop(self) -> None:
        async for device in iterate_queue(self.udev_events):
            if _should_ignore_device(device):
                continue

            try:
                match device.action:
                    case 'add':
                        await self.__handle_udev_add(device)
                    case 'remove':
                        await self.__handle_udev_remove(device)
                    case _:
                        pass
            except Exception as e:
                print('Exception while processing udev event')
                print(e)

    def __on_udev(self) -> None:
        try:
            # Drain the queue; add_reader only guarantees ≥1 event.
            while (device := self.monitor.poll(0)) is not None:
                if device.action in {'add', 'remove'}:
                    self.udev_events.put_nowait(device)
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
        # reload config files for known devices
        for loop in self.device_loops.values():
            loop.reload_mappings()

        # try to load a device that did not have configuration files before
        for device in self.udev_context.list_devices(subsystem='input'):
            if device.device_node in self.device_loops:
                continue

            self.__add_udev_device(device)

    async def __begin_hotkey(self, hotkey: str, /) -> HotkeyActivation | None:
        if (keys := self.context['keys'].get(hotkey)) is None:
            return None

        if isinstance(keys, list):
            keys = keys.copy()

        if isinstance(keys, str):

            async def do_nothing() -> None:
                pass

            async def finish_command() -> None:
                if hotkey == 'exit':
                    await self.__reset_mouse_position()

                proc = await asyncio.create_subprocess_shell(keys)
                command_task = asyncio.create_task(proc.wait(), name=f'command:{keys}')
                self.background_tasks.add(command_task)
                command_task.add_done_callback(self.background_tasks.discard)

            # A command runs only after a real keyup. Cancelling the
            # activation because its device disappeared does nothing.
            return HotkeyActivation(finish_command, do_nothing)

        if hotkey == 'exit':
            await self.__reset_mouse_position()

        _send_keys(self.target, keys, True, self.debug)

        async def release_keys() -> None:
            _send_keys(self.target, keys, False, self.debug)

        # Key codes must be released even when the input device disappears.
        return HotkeyActivation(release_keys, release_keys)

    async def __send_hotkey(self, hotkey: str, delay: int | None, /) -> None:
        if self.debug:
            if delay:
                print(f'Sending {hotkey} with delay {delay}')
            else:
                print(f'Sending {hotkey}')

        if (activation := await self.__begin_hotkey(hotkey)) is None:
            return

        try:
            # time required for emulators (like mame) based on states and not on events
            # (if you go too fast, the event is not seen, so we default to 0.3)
            await asyncio.sleep(delay or 0.3)
        except BaseException:
            await activation.cancel()
            raise
        finally:
            await activation.finish()

    async def __reset_mouse_position(self) -> None:
        await reset_pointer_position(self.target)

    async def __run_tracked_action[**P](
        self,
        action: Callable[P, Awaitable[object]],
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        """Run an asynchronous backend action and track its current task.

        A D-Bus action may still be running when daemon shutdown begins. Closing the
        hotkey device before that action completes could raise an exception or leave
        emitted keys without matching release events. Tracking the current task lets
        shutdown cancel and await the action, giving it an opportunity to release any
        active keys before the device is closed. New actions are ignored after shutdown
        begins.
        """

        if self.stopping:
            return

        task = asyncio.current_task()
        assert task is not None

        self.tracked_backend_tasks.add(task)

        try:
            await action(*args, **kwargs)
        finally:
            self.tracked_backend_tasks.discard(task)

    ## begin ContextBackend

    def set_context(self, context: HotkeysContextMapping, /, include_common: bool = True) -> None:
        self.__set_context(context, include_common=include_common)

    def set_default_context(self) -> None:
        self.__set_context(None, include_common=True)

    def get_context(self) -> HotkeysContext:
        return deepcopy(self.context)

    def get_device_mappings(self) -> dict[tuple[str, str, str, str], tuple[dict[int, str], dict[int, str]]]:
        return dict(device_loop.get_device_mapping_item() for device_loop in self.device_loops.values())

    def reload(self) -> None:
        if not self.context['name']:
            self.set_default_context()
        else:
            self.__reload_device_mappings()

    ## end ContextBackend

    ## begin HotkeyBackend

    async def send_hotkey(self, hotkey: str, delay: int | None, /) -> None:
        await self.__run_tracked_action(self.__send_hotkey, hotkey, delay)

    ## end HotkeyBackend

    ## begin MouseBackend

    async def reset_mouse_position(self) -> None:
        await self.__run_tracked_action(self.__reset_mouse_position)

    ## end MouseBackend

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
            self.__add_udev_device(device)

        # process udev events in a background task
        self.udev_task = asyncio.create_task(self.__udev_loop(), name='udev-input-monitor')

        try:
            async with Service(self):
                try:
                    await asyncio.Event().wait()  # wait forever
                finally:
                    self.stopping = True
        finally:
            loop.remove_reader(self.monitor)

            await cancel_all(*list(self.tracked_backend_tasks))

            self.udev_task.cancel()
            await asyncio.gather(self.udev_task, return_exceptions=True)

            await asyncio.gather(
                # Make a copy of values() since stop() modifies the dict.
                *(loop.stop() for loop in list(self.device_loops.values())),
                return_exceptions=True,
            )

            await cancel_all(*self.background_tasks)

            self.target.close()
