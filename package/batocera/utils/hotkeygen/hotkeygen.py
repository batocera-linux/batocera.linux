#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import select
import signal
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final, TypedDict

import evdev
import pyudev
from evdev import ecodes

if TYPE_CHECKING:
    from collections.abc import Mapping
    from types import FrameType

    class HotkeysContext(TypedDict):
        name: str
        keys: dict[str, list[int] | int | str]


    class JsonHotkeysContext(TypedDict):
        name: str
        keys: dict[str, list[str] | str]


DEVICE_NAME: Final   = "batocera hotkeys"
GDEFAULTCONTEXT_FILE: Final = Path("/etc/hotkeygen/default_context.conf")
GCOMMONCONTEXT_FILE: Final = Path("/etc/hotkeygen/common_context.conf")
GDEFAULTMAPPING_FILE: Final = Path("/etc/hotkeygen/default_mapping.conf")

GCONTEXT_FILE: Final = Path("/var/run/hotkeygen.context")
GPID_FILE: Final     = Path("/var/run/hotkeygen.pid")
GSYSTEM_DIR: Final   = Path("/usr/share/hotkeygen")
GUSER_DIR: Final     = Path("/userdata/system/configs/hotkeygen")

GUSERCOMMONCONTEXT_FILE: Final = GUSER_DIR / Path("common_context.conf")
GUSERDEFAULTMAPPING_FILE: Final = GUSER_DIR / Path("default_mapping.conf")

gdebug = False

ECODES_NAMES: Final[dict[int, str]] = {
    # add BTN_ to that joysticks buttons can run hotkeys (but keep generating only KEY_ events)
    key_code: key_name for key_name, key_code in ecodes.ecodes.items() if key_name.startswith("KEY_") or key_name.startswith("BTN_")
}

# default context is for es
def get_default_context() -> HotkeysContext:
    if GDEFAULTCONTEXT_FILE.exists():
        with GDEFAULTCONTEXT_FILE.open() as file:
            data = json.load(file)
            return load_context(data)
    else:
        return {"name": "", "keys": {}}

def get_common_context_keys() -> dict[str, int|str]:
    keys = {}
    userkeys = {}

    if GCOMMONCONTEXT_FILE.exists():
        with GCOMMONCONTEXT_FILE.open() as file:
            data = json.load(file)
            keys = load_context_keys(data)

    if GUSERCOMMONCONTEXT_FILE.exists():
        with GUSERCOMMONCONTEXT_FILE.open() as file:
            data = json.load(file)
            userkeys = load_context_keys(data)

    return keys | userkeys

def get_context() -> HotkeysContext | None:
    if GCONTEXT_FILE.exists():
        try:
            if gdebug:
                print(f"using default context {GCONTEXT_FILE}")
            with GCONTEXT_FILE.open() as file:
                data = json.load(file)
                context = load_context(data)
                context["keys"] |= get_common_context_keys()
                return context
        except Exception as e:
            print(f"fail to load context file : {e}")
            return None
    else:
        context = get_default_context()
        context["keys"] |= get_common_context_keys()
        if gdebug:
            print("using default context")
            print_context(context)
        return context

def load_context_keys(keys: dict[str, list[str] | str]) -> dict[str, list[int] | int | str]:
    res = {}
    for action, key_code_names in keys.items():
        if isinstance(key_code_names, list):
            codes: list[int] = []
            res[action] = codes
            for x in key_code_names:
                if x in ecodes.ecodes:
                    codes.append(ecodes.ecodes[x])
                else:
                    raise Exception(f"invalid key {x!r}")
        else:
            # string are key if starting by KEY_ else commands (maybe not the best choice, but simple)
            if key_code_names[:4] == "KEY_":
                if key_code_names in ecodes.ecodes:
                    res[action] = ecodes.ecodes[key_code_names]
                else:
                    raise Exception(f"invalid key {data['keys'][action]!r}")
            else:
                # command
                res[action] = key_code_names
    return res

def load_context(data: JsonHotkeysContext) -> HotkeysContext:
    if "name" not in data:
        raise Exception("no name section found")
    if "keys" not in data:
        raise Exception("no keys section found")

    context: HotkeysContext = { "name": data["name"], "keys": {} }
    context["keys"] = load_context_keys(data["keys"])
    if gdebug:
        print_context(context)
    return context

def save_context(context: HotkeysContext, gcontext_file: Path) -> None:
    save: JsonHotkeysContext = { "name": context["name"], "keys": {} }
    for action, key_codes in context["keys"].items():
        if isinstance(key_codes, list):
            save["keys"][action] = [ECODES_NAMES[key] for key in key_codes]
        elif isinstance(key_codes, str):
            save["keys"][action] = key_codes
        else:
            save["keys"][action] = ECODES_NAMES[key_codes]

    with gcontext_file.open("w") as fd:
        json.dump(save, fd, indent=2)

def print_context(context: HotkeysContext) -> None:
    print(f"Context [{context['name']}]:")
    for action, keys in context["keys"].items():
        if isinstance(keys, list):
            print(f"  {action:-<20}-> {[ECODES_NAMES[key] for key in keys]}")
        elif isinstance(keys, str):
            print(f"  {action:-<20}-> command [{keys}]")
        else:
            print(f"  {action:-<20}-> {ECODES_NAMES[keys]}")

def get_device_config_filename(device: evdev.InputDevice) -> str:
    name = re.sub('[^a-zA-Z0-9_]', '', device.name.replace(' ', '_'))
    return f"{name}-{device.info.vendor:02x}-{device.info.product:02x}.mapping"

def get_mapping_full_path(device: evdev.InputDevice) -> Path | None:
    fullpath = None
    fname = get_device_config_filename(device)
    if gdebug:
        print(f"...looking for {GUSER_DIR}/{fname}, {GSYSTEM_DIR}/{fname}")
    if (GUSER_DIR / fname).exists():
        fullpath = GUSER_DIR / fname
    elif (GSYSTEM_DIR / fname).exists():
        fullpath = GSYSTEM_DIR / fname
    return fullpath

def get_mapping(device: evdev.InputDevice) -> dict[int, str]:
    fullpath = get_mapping_full_path(device)

    if fullpath is not None:
        if gdebug:
            print(f"using mapping {fullpath}")
        with fullpath.open() as fd:
            data = json.load(fd)
        return load_mapping(data)
    else:
        data = {}
        userdata = {}
        if GDEFAULTMAPPING_FILE.exists():
            with GDEFAULTMAPPING_FILE.open() as fd:
                data = json.load(fd)
        if GUSERDEFAULTMAPPING_FILE.exists():
            with GUSERDEFAULTMAPPING_FILE.open() as fd:
                userdata = json.load(fd)

        return load_mapping(data | userdata)

def load_mapping(data: dict[str, str]) -> dict[int, str]:
    try:
        mapping: dict[int, str] = {}
        for key, action in data.items():
            if key in ecodes.ecodes:
                mapping[ecodes.ecodes[key]] = action
            else:
                raise Exception(f"invalid key {action!r}")
        return mapping
    except Exception as e:
        print(f"fail to load mapping : {e}")
        return {}

def get_mapping_associations(mapping: Mapping[int, str], caps: dict[int, list[int | tuple[int, evdev.AbsInfo]]]):
    capskeys = set(caps[ecodes.EV_KEY])
    return {key: value for key, value in mapping.items() if key in capskeys}

def print_mapping(
    mapping: Mapping[int, str], associations: Mapping[int, str], context: HotkeysContext | None = None
) -> None:
    for k in mapping:
        if k in associations:
            if context is None:
                print(f"  {ECODES_NAMES[k]:-<15}-> {associations[k]}")
            else:
                if associations[k] in context["keys"]:
                    key_codes = context["keys"][associations[k]]
                    if isinstance(key_codes, list):
                        key_names = [ECODES_NAMES[x] for x in key_codes]
                        print(
                            f"  {ECODES_NAMES[k]:-<15}-> {associations[k]:-<15}-> {key_names}"
                        )
                    if isinstance(key_codes, str):
                        print(f"  {ECODES_NAMES[k]:-<15}-> {associations[k]:-<15}-> {key_codes}")
                    else:
                        print(f"  {ECODES_NAMES[k]:-<15}-> {associations[k]:-<15}-> {ECODES_NAMES[key_codes]}")
                else:
                    print(f"  {ECODES_NAMES[k]:-<15}-> {associations[k]:15}")


def send_keys(target: evdev.UInput, keys: int | list[int] | str) -> None:
    if isinstance(keys, list):
        for x in keys:
            target.write(ecodes.EV_KEY, x, 1)
            target.syn()
        # time required for emulators (like mame) based on states and not on events
        # (if you go too fast, the event is not seen)
        time.sleep(0.1)
        for x in keys:
            target.write(ecodes.EV_KEY, x, 0)
            target.syn()
    else:
        target.write(ecodes.EV_KEY, keys, 1)
        target.syn()
        # time required for emulators (like mame) based on states and not on events
        # (if you go too fast, the event is not seen)
        time.sleep(0.1)
        target.write(ecodes.EV_KEY, keys, 0)
        target.syn()

def do_send(key: str) -> None:
    context = get_context()
    sender_keys: list[int] = []
    if context is not None and key in context["keys"]:
        keys = context["keys"][key]
        if isinstance(keys, str):
            os.system(keys)
        else:
            if isinstance(keys, list):
                sender_keys.extend(keys)
            else:
                sender_keys.append(keys)
            sender = evdev.UInput(name="virtual keyboard", events={ ecodes.EV_KEY: sender_keys })
            send_keys(sender, sender_keys)
    else:
        print(f"unknown action {key}")

def read_pid() -> str:
    with GPID_FILE.open() as fd:
        return fd.read().replace('\n', '')

def do_new_context(context_name: str | None = None, context_json: str | None = None) -> None:
    if context_name is not None and context_json is not None:
        context = load_context({
            'name': context_name,
            'keys': json.loads(context_json)
        })
        # update the config file
        save_context(context, GCONTEXT_FILE)
    else:
        if GCONTEXT_FILE.exists():
            GCONTEXT_FILE.unlink()

    # inform the process
    pid = int(read_pid())
    os.kill(pid, signal.SIGHUP)


def do_list() -> None:
    context = get_context()

    udev_context = pyudev.Context()

    if context is not None:
        print_context(context)

    for device in udev_context.list_devices(subsystem='input'):
        if device.device_node is not None and device.device_node.startswith("/dev/input/event"):
            dev = evdev.InputDevice(device.device_node)
            if dev.name != DEVICE_NAME:
                caps = dev.capabilities()
                if ecodes.EV_KEY in caps:
                    mapping = get_mapping(dev)
                    associations = get_mapping_associations(mapping, caps)

                    fullpath = get_mapping_full_path(dev)
                    if fullpath:
                        print(f"# device {device.device_node} [{dev.name}] ({fullpath})")
                    else:
                        fname = get_device_config_filename(dev)
                        print(f"# device {device.device_node} [{dev.name}] (no {fname} file found)")
                    if associations:
                        print_mapping(mapping, associations, context)

@dataclass(slots=True)
class Daemon:
    permanent: bool = field(kw_only=True)

    context: HotkeysContext | None = field(init=False, default=None)
    running: bool = field(init=False, default=False)
    input_devices: dict[str, evdev.InputDevice] = field(init=False, default_factory=dict)
    input_devices_by_fd: dict[int, evdev.InputDevice] = field(init=False, default_factory=dict)
    mappings_by_fd: dict[int, dict[int, str]] = field(init=False, default_factory=dict)
    udev_context: pyudev.Context = field(init=False)
    monitor: pyudev.Monitor = field(init=False)
    poll: select.poll = field(init=False)
    target: evdev.UInput = field(init=False)

    def __post_init__(self) -> None:
        self.udev_context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.udev_context)
        self.monitor.filter_by(subsystem='input')

        self.poll = select.poll()

        # target virtual keyboard
        self.target = evdev.UInput(
            name=DEVICE_NAME, events={ ecodes.EV_KEY: [x for x in range(ecodes.KEY_MAX) if x in ECODES_NAMES and ECODES_NAMES[x][:4] == "KEY_" ] }
        )

    def __handle_actions(self, action: str, device: pyudev.Device) -> None:
        if device.device_node is not None and device.device_node.startswith("/dev/input/event"):
            if action == "add":
                input_device = evdev.InputDevice(device.device_node)

                if input_device.name != DEVICE_NAME:
                    capabilities = input_device.capabilities()

                    if ecodes.EV_KEY in capabilities:
                        mapping = get_mapping(input_device)
                        associations = get_mapping_associations(mapping, capabilities)

                        if associations:
                            if gdebug:
                                print(f"Adding device {device.device_node}: {input_device.name}")
                                print_mapping(mapping, associations)

                            self.input_devices[device.device_node] = input_device
                            self.input_devices_by_fd[input_device.fileno()] = input_device
                            self.mappings_by_fd[input_device.fileno()] = mapping
                            self.poll.register(input_device, select.POLLIN)
            elif action == "remove":
                input_device = self.input_devices.get(device.device_node)

                if input_device is not None:
                    if gdebug:
                        print(f"Removing device {device.device_node}: {input_device.name}")

                    self.poll.unregister(input_device)
                    del self.mappings_by_fd[input_device.fileno()]
                    del self.input_devices_by_fd[input_device.fileno()]
                    del self.input_devices[device.device_node]

    def __handle_event(self, event: evdev.InputEvent, action: str) -> None:
        if self.context is not None and action in self.context["keys"]:
            keys = self.context["keys"][action]
            if gdebug:
                print(f"code:{event.code}, value:{event.value}, action:{action}")
            if isinstance(keys, str):
                os.system(keys)
            else:
                send_keys(self.target, keys)

    def __write_pid(self) -> None:
        with GPID_FILE.open("w") as fd:
            fd.write(str(os.getpid()))

    def __handle_sighup(self, signum: int, frame: FrameType | None) -> None:
        self.context = get_context()

    def run(self) -> None:
        if self.running:
            raise Exception("already running!")

        self.running = True
        self.context = get_context()

        # permanent : write a pid so that new configuration can apply
        if self.permanent:
            self.__write_pid()

        # monitor all udev devices
        self.monitor.start()
        self.poll.register(self.monitor, select.POLLIN)

        # adding existing devices in the poll
        for device in self.udev_context.list_devices(subsystem='input'):
            self.__handle_actions('add', device)

        # to read new contexts
        signal.signal(signal.SIGHUP, self.__handle_sighup)

        # read all devices
        while True:
            for fd, _ in self.poll.poll():
                try:
                    if fd == self.monitor.fileno():
                        (action, device) = self.monitor.receive_device()
                        self.__handle_actions(action, device)
                    else:
                        event = self.input_devices_by_fd[fd].read_one()
                        if (
                            event is not None and
                            event.type == ecodes.EV_KEY and
                            event.value == 0 and  # limit to key down
                            event.code in self.mappings_by_fd[fd]
                        ):
                            self.__handle_event(event, self.mappings_by_fd[fd][event.code])
                except (OSError):
                    if fd == self.monitor.fileno():
                        raise
                    else:
                        # error on a single device
                        input_device = self.input_devices_by_fd[fd]
                        print(f"error on device {input_device.name} ({input_device.path}), closing.")
                        self.poll.unregister(input_device)
                        del self.mappings_by_fd[fd]
                        del self.input_devices_by_fd[fd]
                        del self.input_devices[input_device.path]
                        input_device.close()
                except:
                    self.target.close()
                    raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="hotkeygen")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--send")
    parser.add_argument("--default-context", action="store_true")
    parser.add_argument("--new-context", nargs=2, metavar=("new-context-name", "new-context-json"))
    parser.add_argument("--permanent", action="store_true")
    args = parser.parse_args()
    if args.debug:
        gdebug = True

    if args.list:
        do_list()
    elif args.send is not None:
        do_send(args.send)
    elif args.new_context is not None:
        new_context_name, new_context_json = args.new_context
        do_new_context(new_context_name, new_context_json)
    elif args.default_context:
        do_new_context()
    else:
        Daemon(permanent=args.permanent).run()
#####
