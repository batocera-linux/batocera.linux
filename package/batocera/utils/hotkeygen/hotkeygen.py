#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import select
import signal
import time
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
        keys: dict[str, list[int] | int]


    class JsonHotkeysContext(TypedDict):
        name: str
        keys: dict[str, list[str] | str]


DEVICE_NAME: Final   = "batocera hotkeys"
GCONTEXT_FILE: Final = Path("/var/run/hotkeygen.context")
GPID_FILE: Final     = Path("/var/run/hotkeygen.pid")
GSYSTEM_DIR: Final   = Path("/usr/share/hotkeygen")
GUSER_DIR: Final     = Path("/userdata/system/configs/hotkeygen")

gdebug = False
gcontext: HotkeysContext | None = None

ECODES_NAMES: Final[dict[int, str]] = {
    key_code: key_name for key_name, key_code in ecodes.ecodes.items() if key_name.startswith("KEY_")
}

KNOWN_ACTIONS: Final = {
    "exit", "coin", "menu", "files", "save_state", "restore_state", "next_slot", "previous_slot", "screenshot"
}

# default context is for es
def get_default_context() -> HotkeysContext:
    return {
        "name": "emulationstation",
        "keys": {
            "exit": ecodes.KEY_ESC,
            "menu": ecodes.KEY_SPACE,
            "files": ecodes.KEY_F1
        }
    }

def get_context() -> HotkeysContext | None:
    if GCONTEXT_FILE.exists():
        try:
            if gdebug:
                print(f"using default context {GCONTEXT_FILE}")
            with GCONTEXT_FILE.open() as file:
                data = json.load(file)
                return load_context(data)
        except Exception as e:
            print(f"fail to load context file : {e}")
            return None
    else:
        context = get_default_context()
        if gdebug:
            print("using default context")
            print_context(context)
        return context

def load_context(data: JsonHotkeysContext) -> HotkeysContext:
    if "name" not in data:
        raise Exception("no name section found")
    if "keys" not in data:
        raise Exception("no keys section found")

    context: HotkeysContext = { "name": data["name"], "keys": {} }
    for action, key_code_names in data["keys"].items():
        if action in KNOWN_ACTIONS:
            if isinstance(key_code_names, list):
                codes: list[int] = []
                context["keys"][action] = codes
                for x in key_code_names:
                    if x in ecodes.ecodes:
                        codes.append(ecodes.ecodes[x])
                    else:
                        raise Exception(f"invalid key {x!r}")
            else:
                if key_code_names in ecodes.ecodes:
                    context["keys"][action] = ecodes.ecodes[key_code_names]
                else:
                    raise Exception(f"invalid key {data['keys'][action]!r}")
        else:
            raise Exception(f"invalid entry '{action}'")

    if gdebug:
        print_context(context)
    return context

def save_context(context: HotkeysContext, gcontext_file: Path) -> None:
    save: JsonHotkeysContext = { "name": context["name"], "keys": {} }
    for action, key_codes in context["keys"].items():
        if isinstance(key_codes, list):
            save["keys"][action] = [ECODES_NAMES[key] for key in key_codes]
        else:
            save["keys"][action] = ECODES_NAMES[key_codes]

    with gcontext_file.open("w") as fd:
        json.dump(save, fd, indent=2)

def print_context(context: HotkeysContext) -> None:
    print(f"Context [{context['name']}]:")
    for action, keys in context["keys"].items():
        if isinstance(keys, list):
            print(f"  {action:-<15}-> {[ECODES_NAMES[key] for key in keys]}")
        else:
            print(f"  {action:-<15}-> {ECODES_NAMES[keys]}")

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
        # default for all inputs
        return {
            ecodes.KEY_EXIT:     "exit",
            ecodes.KEY_EURO:     "coin",
            ecodes.KEY_MENU:     "menu",
            ecodes.KEY_FILE:     "files",
            ecodes.KEY_SAVE:     "save_state",
            ecodes.KEY_SEND:     "restore_state",
            ecodes.KEY_NEXT:     "next_slot",
            ecodes.KEY_PREVIOUS: "previous_slot",
            ecodes.KEY_SCREEN:   "screenshot"
        }

def load_mapping(data: dict[str, str]) -> dict[int, str]:
    try:
        mapping: dict[int, str] = {}
        for key, action in data.items():
            if action in KNOWN_ACTIONS:
                if key in ecodes.ecodes:
                    mapping[ecodes.ecodes[key]] = action
                else:
                    raise Exception(f"invalid key {action!r}")
            else:
                raise Exception(f"invalid entry {action!r}")
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
                    else:
                        print(f"  {ECODES_NAMES[k]:-<15}-> {associations[k]:-<15}-> {ECODES_NAMES[key_codes]}")
                else:
                    print(f"  {ECODES_NAMES[k]:-<15}-> {associations[k]:15}")

def handle_actions(
    devices: dict[str, evdev.InputDevice],
    nodes_by_fd: dict[int, str],
    mappings: dict[int, dict[int, str]],
    poll: select.poll,
    action: str,
    device: pyudev.Device
) -> None:
    if device.device_node is not None and device.device_node.startswith("/dev/input/event"):
        if action == "add":
            dev = evdev.InputDevice(device.device_node)
            if dev.name != DEVICE_NAME:
                caps = dev.capabilities()
                if ecodes.EV_KEY in caps:
                    mapping = get_mapping(dev)
                    associations = get_mapping_associations(mapping, caps)
                    if associations:
                        if gdebug:
                            print(f"Adding device {device.device_node}: {dev.name}")
                            print_mapping(mapping, associations)
                        devices[device.device_node] = dev
                        nodes_by_fd[dev.fileno()] = device.device_node
                        mappings[dev.fileno()] = mapping
                        poll.register(dev, select.POLLIN)
        elif action == "remove":
            if device.device_node in devices:
                if gdebug:
                    print(f"Removing device {device.device_node}: {devices[device.device_node].name}")
                poll.unregister(devices[device.device_node])
                del nodes_by_fd[devices[device.device_node].fileno()]
                del mappings[devices[device.device_node].fileno()]
                del devices[device.device_node]

def handle_event(target: evdev.UInput, event: evdev.InputEvent, action: str, context: HotkeysContext | None) -> None:
    if context is not None and action in context["keys"]:
        if gdebug:
            print(f"code:{event.code}, value:{event.value}, action:{action}")
        send_keys(target, context["keys"][action])

def send_keys(target: evdev.UInput, keys: int | list[int]) -> None:
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
    if key not in KNOWN_ACTIONS:
        print(f"unknown action {KNOWN_ACTIONS}")
        exit(1)

    context = get_context()
    sender_keys: list[int] = []
    if context is not None and key in context["keys"]:
        keys = context["keys"][key]
        if isinstance(keys, list):
            sender_keys.extend(keys)
        else:
            sender_keys.append(keys)
    sender = evdev.UInput(name="virtual keyboard", events={ ecodes.EV_KEY: sender_keys })
    send_keys(sender, sender_keys)

def read_pid() -> str:
    with GPID_FILE.open() as fd:
        return fd.read().replace('\n', '')

def write_pid() -> None:
    with GPID_FILE.open("w") as fd:
        fd.write(str(os.getpid()))

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

def signal_sigup(signum: int, frame: FrameType | None) -> None:
    global gcontext
    gcontext = get_context()

def do_list() -> None:
    gcontext = get_context()

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='input')

    if gcontext is not None:
        print_context(gcontext)

    for device in context.list_devices(subsystem='input'):
        if device.device_node is not None and device.device_node.startswith("/dev/input/event"):
            dev = evdev.InputDevice(device.device_node)
            if dev.name != DEVICE_NAME:
                caps = dev.capabilities()
                if ecodes.EV_KEY in caps:
                    mapping = get_mapping(dev)
                    associations = get_mapping_associations(mapping, caps)
                    if associations:
                        fullpath = get_mapping_full_path(dev)
                        fname = get_device_config_filename(dev)
                        if fullpath:
                            print(f"# device {device.device_node} [{dev.name}] ({fullpath})")
                        else:
                            print(f"# device {device.device_node} [{dev.name}] (no {fname} file found)")
                        print_mapping(mapping, associations, gcontext)

def run(args: argparse.Namespace) -> None:
    global gcontext

    devices: dict[str, evdev.InputDevice] = {}
    nodes_by_fd: dict[int, str] = {}
    mappings: dict[int, dict[int, str]] = {}

    gcontext = get_context()

    # permanent : write a pid so that new configuration can apply
    if args.permanent:
        write_pid()

    # monitor all udev devices
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='input')
    monitor.start()

    poll = select.poll()
    poll.register(monitor, select.POLLIN)

    # adding existing devices in the poll
    for device in context.list_devices(subsystem='input'):
        handle_actions(devices, nodes_by_fd, mappings, poll, "add", device)

    # target virtual keyboard
    target_keys = [x for x in range(ecodes.KEY_MAX) if x in ECODES_NAMES]
    target = evdev.UInput(name=DEVICE_NAME, events={ ecodes.EV_KEY: target_keys })

    # to read new contexts
    signal.signal(signal.SIGHUP, signal_sigup)

    # read all devices
    while True:
        for fd, _ in poll.poll():
            try:
                if fd == monitor.fileno():
                    (action, device) = monitor.receive_device()
                    handle_actions(devices, nodes_by_fd, mappings, poll, action, device)
                else:
                    event = devices[nodes_by_fd[fd]].read_one()
                    if (
                        event is not None and
                        event.type == ecodes.EV_KEY and
                        event.value == 0 and  # limit to key down
                        event.code in mappings[fd]
                    ):
                        handle_event(target, event, mappings[fd][event.code], gcontext)
            except (OSError, KeyError):
                pass # ok, error on the device
            except:
                target.close()
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
        run(args)
#####
