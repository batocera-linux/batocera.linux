#!/usr/bin/env python3

import yaml
import argparse
import json
import subprocess
import sys

import pyudev
import evdev
import re
from pathlib import Path

class KeyboardController:

    def generateRules(self, configFile) -> str:
        rules = ""
        config = {}
        with open(configFile, 'r') as file:
            config = yaml.safe_load(file)

        if "target_devices" not in config:
            raise Exception("missing target_devices entry in config file")
        for target_device in config["target_devices"]:
            if "name" not in target_device:
                raise Exception("missing name entry in target_devices section")
            if "type" not in target_device:
                raise Exception("missing type entry in target_devices section")
            if target_device["type"] not in ["joystick", "hotkeys"]:
                raise Exception("invalid type " + target_device["type"])

            if target_device["type"] == "hotkeys":
                # hide this one, hotkeys will be found by hotgenkey
                rules += "SUBSYSTEM==\"input\", KERNEL==\"event*\", ACTION==\"add\", ATTRS{{name}}==\"{}\", ".format(target_device["name"])
                rules += "ENV{ID_INPUT_JOYSTICK}=\"0\", ENV{ID_INPUT_KEYBOARD}=\"0\", ENV{ID_INPUT_KEY}=\"0\"\n"
            elif target_device["type"] == "joystick":
                rules += "SUBSYSTEM==\"input\", KERNEL==\"event*\", ACTION==\"add\", ATTRS{{name}}==\"{}\", ".format(target_device["name"])
                rules += "ENV{ID_INPUT_JOYSTICK}=\"1\", ENV{ID_INPUT_KEYBOARD}=\"0\", ENV{ID_INPUT_KEY}=\"0\"\n"
        return rules

    def generateCommand(self, configFile, inputFile) -> list[str]:
        config = {}
        with open(configFile, 'r') as file:
            config = yaml.safe_load(file)

        cmd = ["evsieve", "--input", inputFile, "persist=exit" ]

        if "target_devices" not in config:
            raise Exception("missing target_devices entry in config file")
        for target_device in config["target_devices"]:
            if "name" not in target_device:
                raise Exception("missing name entry in target_devices section")
            if "type" not in target_device:
                raise Exception("missing type entry in target_devices section")
            if "mapping" not in target_device:
                raise Exception("missing mapping entry in target_devices section")
            if target_device["type"] not in ["joystick", "hotkeys"]:
                raise Exception("invalid type " + target_device["type"])

            # check mappings and values
            for mapping, value in target_device["mapping"].items():
                mappingParts = mapping.split(':')
                valueParts   = value.split(':')
                if len(mappingParts) not in [2, 3]:
                    raise Exception("invalid key "+mapping)
                if len(valueParts) not in [2, 3]:
                    raise Exception("invalid key "+value)
                if mappingParts[0] not in ["key", "abs", "btn"]:
                    raise Exception("invalid key type "+mapping)
                if valueParts[0] not in ["key", "abs", "btn"]:
                    raise Exception("invalid key type "+value)

            # add mappings
            for mapping, value in target_device["mapping"].items():
                mappingParts = mapping.split(':')
                mappingtypename = mappingParts[0] + ":" + mappingParts[1]
                valueParts = value.split(':')
                valuetypename = valueParts[0] + ":" + valueParts[1]
                cmd.extend(["--block", "{}:2".format(mappingtypename)]) # block the repeat keys

                if len(mappingParts) == 2 and len(valueParts) == 2:
                    cmd.extend(["--map", "yield", mapping, value])
                elif len(mappingParts) == 2 and len(valueParts) == 3:
                    cmd.extend(["--map", "yield", "{}:1".format(mapping), value])
                    cmd.extend(["--map", "yield", "{}:0".format(mapping), "{}:0".format(valuetypename)])
                elif len(mappingParts) == 3 and len(valueParts) == 2:
                    cmd.extend(["--map", "yield", mapping, "{}:1".format(value)])
                    cmd.extend(["--map", "yield", "{}:0".format(mappingtypename), "{}:0".format(value)])

            # output device
            cmd.extend(["--output", "name={}".format(target_device["name"]), "device-id=ba10:ce8a"])

            # output filter (remove doubles)
            keyslist = {}
            for mapping, value in target_device["mapping"].items():
                valueParts = value.split(':')
                valuetypename = valueParts[0] + ":" + valueParts[1]
                keyslist[valuetypename] = True
            for mapping in keyslist:
                cmd.append(mapping)
        return cmd

    # the search function has more sens in keyboardToPadsLauncher, but nicer to write in python
    def search(self):
        udev_context = pyudev.Context()
        for device in udev_context.list_devices(subsystem='input'):
            if device.device_node is not None and device.device_node.startswith("/dev/input/event"):
                dev = evdev.InputDevice(device.device_node)
                if "ID_INPUT_KEYBOARDTOPADS" in device.properties and device.properties["ID_INPUT_KEYBOARDTOPADS"] == "1":
                    safename = re.sub(r'[^a-zA-Z0-9]', '', dev.name) + f".v{dev.info.vendor:04x}.p{dev.info.product:04x}.yml"
                    print(f"device {device.device_node} : \"{dev.name}\"")
                    print(f"  config file name : {safename}")
                    sysconfig = Path(f"/usr/share/keyboardToPads/inputs/{safename}")
                    if sysconfig.exists():
                        print(f"  system config found at {sysconfig}")
                    userconfig = Path(f"/userdata/system/configs/keyboardToPads/inputs/{safename}")
                    if userconfig.exists():
                        print(f"  user config found at {userconfig}")
                        try:
                            cmd = KeyboardController().generateCommand(userconfig, device.device_node)
                        except Exception as e:
                            print(f"\n\nSome errors were found in the user configuration file {userconfig}:")
                            print(e)
                    else:
                        print(f"  you can create a custom config at {userconfig}. Take example on files in /usr/share/keyboardToPads/inputs.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="keyboardToPads")
    parser.add_argument("--search", action="store_true")
    parser.add_argument("--config")
    parser.add_argument("--input")
    parser.add_argument("--run",    action="store_true")
    parser.add_argument("--rules",  action="store_true")
    args = parser.parse_args()

    if args.search is None and args.config is None:
        parser.error("at least one of --search and --config required")

    if args.search:
        KeyboardController().search()
    else:
        if args.run and args.input:
            cmd = KeyboardController().generateCommand(args.config, args.input)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            print(out.decode())
            print(err.decode())
            sys.exit(exitcode)
        elif args.rules:
            rules = KeyboardController().generateRules(args.config)
            print(rules)
        else:
            parser.error("with --config, at least one of --run and --rules required")
            parser.print_help()
