#!/usr/bin/env python3

import argparse
import evdev
from evdev import ecodes
import pyudev
import select
import datetime
import sys
import os
import re
from pathlib import Path
import json

DEVICES_EXCLUSION = ["batocera hotkeys"]
CONFIG_DIR = Path("/userdata/system/configs/hotkeygen")
HOTKEYGEN_MAPPING = Path("/etc/hotkeygen/default_mapping.conf")

ECODES_NAMES = {
    # add BTN_ to that joysticks buttons can run hotkeys (but keep generating only KEY_ events)
    key_code: key_name for key_name, key_code in ecodes.ecodes.items() if key_name.startswith("KEY_") or key_name.startswith("BTN_")
}

def add_devices(poll, udev_context):
        input_devices_by_fd = {}
        # filter devices to add
        for device in udev_context.list_devices(subsystem='input'):
                if device.device_node is not None and device.device_node.startswith("/dev/input/event"):
                        input_device = evdev.InputDevice(device.device_node)
                        if input_device.name not in DEVICES_EXCLUSION:
                                capabilities = input_device.capabilities()
                                if ecodes.EV_KEY in capabilities:
                                        if gdebug:
                                                print(f"listening device {device.device_node:<18} {input_device.name}", file=sys.stderr)
                                        input_devices_by_fd[input_device.fileno()] = input_device
                                        poll.register(input_device, select.POLLIN)
        return input_devices_by_fd

def remove_devices(poll, input_devices_by_fd):
        for fd in list(input_devices_by_fd):
                input_device = input_devices_by_fd[fd]
                del input_devices_by_fd[fd]
                try:
        	        poll.unregister(input_device)
        	        input_device.close()
                except:
                        pass

def handle_event(device: evdev.InputDevice, event: evdev.InputEvent, pressures: dict) -> None:
        if event.type == ecodes.EV_KEY:
                config_name = get_device_config_filename(device)
                if event.code in ECODES_NAMES:
                        code_name = ECODES_NAMES[event.code]
                        if gdebug:
                                print(f"{device.path:<20} {code_name:<16} {device.name:<40} {config_name}", file=sys.stderr)
                        if device.path not in pressures:
                                pressures[device.path] = { "name": device.name, "config": config_name, "keys": {} }
                        if code_name not in pressures[device.path]["keys"]:
                                pressures[device.path]["keys"][code_name] = { "count": 0 }
                        pressures[device.path]["keys"][code_name]["count"] += 1
                        os.system("batocera-flash-screen 0.1 '#ff00ff'")

def get_device_config_filename(device: evdev.InputDevice) -> str:
    name = re.sub('[^a-zA-Z0-9_]', '', device.name.replace(' ', '_'))
    return f"{name}-{device.info.vendor:02x}-{device.info.product:02x}.mapping"

def do_output(pressures, ncount):
        if not sys.stdout.isatty():
                print("<keys>")
        for evt in pressures:
                for key in pressures[evt]["keys"]:
                        if pressures[evt]["keys"][key]["count"] == ncount:
                                if sys.stdout.isatty():
                                        print(f"{evt:<20} {key:<16} {pressures[evt]['name']:<40} {pressures[evt]['config']}")
                                else:
                                        print(f"<key event=\"{evt}\" key=\"{key}\" config=\"{pressures[evt]['config']}\" count=\"{pressures[evt]['keys'][key]['count']}\" />")
        if not sys.stdout.isatty():
                print("</keys>")

def do_detect(ncount, duration):
        udev_context = pyudev.Context()
        poll = select.poll()
        input_devices_by_fd = add_devices(poll, udev_context)
        start_time = datetime.datetime.now()
        pressures = {}

        # read all devices
        if sys.stdout.isatty():
                print(f"Press {ncount} times buttons to filter", file=sys.stderr)
        while datetime.datetime.now() - start_time < datetime.timedelta(seconds=duration):
                try:
                	for fd, _ in poll.poll(100):
                	    try:
                	            event = input_devices_by_fd[fd].read_one()
                	            if (
                	                event is not None and
                	                event.type == ecodes.EV_KEY
                	            ):
                	                if event.value == 1:
                	                    handle_event(input_devices_by_fd[fd], event, pressures)
                	    except (Exception) as e:
                	            # error on a single device
                	            if fd in input_devices_by_fd:
                	                    input_device = input_devices_by_fd[fd]
                	                    if not (isinstance(e, OSError) and e.errno == errno.ENODEV):
                	                        print(e)
                	                        print(f"error on device {input_device.name} ({input_device.path}), closing.")
                	                    del input_devices_by_fd[fd]
                	                    try:
                	                        poll.unregister(input_device)
                	                        input_device.close()
                	                    except:
                	                        pass
                except (KeyboardInterrupt) as e:
                        remove_devices(poll, input_devices_by_fd)
                        return
        remove_devices(poll, input_devices_by_fd)
        do_output(pressures, ncount)

def getConfigFancyName(file):
        # remove the vip/pid, extension and replace _ by spaces
        x = re.sub(r'-[^-]*-[^-]*\.mapping', '', file.replace("_", " "))
        # replace multiple spaces by single ones
        x = re.sub('[ ]+', ' ', x)
        return x.strip()

def do_list():
        n = 0
        if not sys.stdout.isatty():
                print("<hotkeys>")
        if os.path.exists(CONFIG_DIR):
                for file in os.listdir(CONFIG_DIR):
                        path = Path(os.path.join(CONFIG_DIR, file))
                        if os.path.isfile(path) and file.endswith(".mapping"):
                                values = {}
                                with path.open() as fd:
                                        values = json.load(fd)
                                fancy_name = getConfigFancyName(file)
                
                                if sys.stdout.isatty():
                                        if n != 0:
                                                print("")
                                        print(f"{fancy_name} ({file})")
                                        for key in values:
                                                action = values[key]
                                                print(f"  {key:<16} {action:<16}")
                                else:
                                        print(f"  <device fancy_name=\"{fancy_name}\" config=\"{file}\">")
                                        for key in values:
                                                action = values[key]
                                                print(f"    <hotkey key=\"{key}\" action=\"{action}\" />")
                                        print("  </device>")
                        n = n+1
        if not sys.stdout.isatty():
                print("</hotkeys>")

def do_set(config, key, action):
        path = Path(os.path.join(CONFIG_DIR, config))
        if not config.endswith(".mapping"):
                print("invalid configuration file", file=sys.stderr)
                return

        values = {}
        if os.path.isfile(path):
                with path.open() as fd:
                        values = json.load(fd)
        if action == "none":
                values[key] = ""
        elif action is None:
                if key in values:
                        del values[key]
        else:
                values[key] = action
        if not os.path.exists(CONFIG_DIR):
                os.makedirs(CONFIG_DIR)
        with open(path, "w") as fd:
                json.dump(values, fd, indent=4)

def list_values(hotkeys_mapping):
    for key in sorted(hotkeys_mapping["by_names"]):
        print(key)

def read_hotkey_mapping(hotkey_mapping_file: Path):
    mapping = json.loads(hotkey_mapping_file.read_text())
    by_keys = mapping
    by_names = {}
    for m in by_keys:
        by_names[by_keys[m]] = m
    return { "by_keys": by_keys, "by_names": by_names}

gdebug = False
ncount = 2
duration = 4 # x seconds
parser = argparse.ArgumentParser(prog="batocera-hotkeys")
parser.add_argument("--debug", action="store_true")
parser.add_argument("--count", type=int, help="detection count")
parser.add_argument("--duration", type=int, help="detection duration")
parser.add_argument("--detect", action="store_true")
parser.add_argument("--values", action="store_true")
parser.add_argument("--set", action="store_true")
parser.add_argument("--remove", action="store_true")
parser.add_argument("--config", type=str, help="config to set")
parser.add_argument("--key", type=str, help="key to set")
parser.add_argument("--action", type=str, help="action to set")
args = parser.parse_args()
if args.debug:
        gdebug = True
if args.count:
        ncount = args.count
if args.duration:
        duration = args.duration

if args.detect:
        do_detect(ncount, duration)
elif args.values:
        hotkeys_mapping = read_hotkey_mapping(HOTKEYGEN_MAPPING)
        list_values(hotkeys_mapping)
elif args.remove:
        if args.config and args.key:
                do_set(args.config, args.key, None)
                os.system("hotkeygen --reload") # reload the configuration
        else:
                print("remove requires config and key arguments", file=sys.stderr)
elif args.set:
        if args.config and args.key and args.action:
                do_set(args.config, args.key, args.action)
                os.system("hotkeygen --reload") # reload the configuration
        else:
                print("set requires config, key and action arguments", file=sys.stderr)
else:
        do_list()
###
