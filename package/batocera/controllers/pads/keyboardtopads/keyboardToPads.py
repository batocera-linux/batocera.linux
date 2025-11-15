#!/usr/bin/env python3

import yaml
import argparse
import json
import subprocess
import sys
import os

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

    def getConfigFancyName(self, file):
        # remove the vip/pid, extension and replace _ by spaces
        x = re.sub(r'\.v[^\.]*\.p[^\.]*\.yml', '', file.replace("_", " "))
        # replace multiple spaces by single ones
        x = re.sub('[ ]+', ' ', x)
        return x.strip()

    def read_config(self, config_name):
        config = {}

        sysconfig = Path(f"/usr/share/keyboardToPads/inputs/{config_name}")
        userconfig = Path(f"/userdata/system/configs/keyboardToPads/inputs/{config_name}")

        configFile = None
        if sysconfig.exists():
            configFile = sysconfig
        if userconfig.exists():
            configFile = userconfig

        # fill if possible
        if configFile is not None and configFile.exists():
            with open(configFile, 'r') as file:
                config = yaml.safe_load(file)

        return config

    def save_config(self, config_name, config):
        userconfig = Path(f"/userdata/system/configs/keyboardToPads/inputs/{config_name}")
        with open(userconfig, 'w') as file:
            yaml.dump(config, file)

    def get_config(self, config_name):
        config = self.read_config(config_name)

        fancy_name = self.getConfigFancyName(config_name)

        print(f"<keyboardtopad name=\"{fancy_name}\" config=\"{config_name}\">")
        if "target_devices" in config:
            for infos in config["target_devices"]:
                if "name" in infos and "type" in infos and "mapping" in infos:
                    device_name = infos["name"]
                    device_type = infos["type"]
                    print(f"  <device name=\"{device_name}\" type=\"{device_type}\">")
                    for key in infos["mapping"]:
                        key_value = infos["mapping"][key]
                        print(f"    <key name=\"{key}\" value=\"{key_value}\" />")
                    print(f"  </device>")
        print("</keyboardtopad>")

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
        if not sys.stdout.isatty():
            print("<keyboardtopads>")
        for device in udev_context.list_devices(subsystem='input'):
            if device.device_node is not None and device.device_node.startswith("/dev/input/event"):
                dev = evdev.InputDevice(device.device_node)
                if "ID_INPUT_KEYBOARDTOPADS" in device.properties and device.properties["ID_INPUT_KEYBOARDTOPADS"] == "1":
                    device_name = re.sub(r'[^a-zA-Z0-9]', '', dev.name)
                    safe_name = device_name + f".v{dev.info.vendor:04x}.p{dev.info.product:04x}.yml"
                    if not sys.stdout.isatty():
                        print(f"  <device name=\"{dev.name}\" config=\"{safe_name}\" device=\"{device.device_node}\" />");
                    if sys.stdout.isatty():
                        print(f"device {device.device_node} : \"{dev.name}\"")
                        print(f"  config file name : {safe_name}")
                    sysconfig = Path(f"/usr/share/keyboardToPads/inputs/{safe_name}")
                    if sysconfig.exists():
                        if sys.stdout.isatty():
                            print(f"  system config found at {sysconfig}")
                    userconfig = Path(f"/userdata/system/configs/keyboardToPads/inputs/{safe_name}")
                    if userconfig.exists():
                        if sys.stdout.isatty():
                            print(f"  user config found at {userconfig}")
                        try:
                            cmd = KeyboardController().generateCommand(userconfig, device.device_node)
                        except Exception as e:
                            print(f"\n\nSome errors were found in the user configuration file {userconfig}:", file=sys.stderr)
                            print(e, file=sys.stderr)
                    else:
                        if sys.stdout.isatty():
                            print(f"  you can create a custom config at {userconfig}. Take example on files in /usr/share/keyboardToPads/inputs.", file=sys.stderr)
        if not sys.stdout.isatty():
            print("</keyboardtopads>")

    def do_set(self, config_name, device_number, device_name, device_type, device_keep, values):
        config = self.read_config(config_name)
        if "target_devices" not in config:
            config["target_devices"] = []

        if device_type is None:
            raise Exception("device type not set")

        # truncate the number of devices
        if device_keep is not None:
            new_target_devices = []
            for k,d in enumerate(config["target_devices"]):
                if d["type"] != device_type or k < device_keep:
                    new_target_devices.append(d)
            config["target_devices"] = new_target_devices
        else:
            if device_number is None:
                raise Exception("device number not set")
            # add the device if needed
            ndevices = 0
            for d in config["target_devices"]:
                if d["type"] == device_type:
                    ndevices += 1
            for i in range(device_number-ndevices+1):
                config["target_devices"].append({"name": "", "type": device_type, "mapping": []})

            # assign values
            ndevices = 0
            for k,d in enumerate(config["target_devices"]):
                if d["type"] == device_type:
                    if device_number == ndevices:
                        if device_name is not None:
                            config["target_devices"][k]["name"] = device_name
                            confs = values.split(",")
                            new_mapping = {}
                            for conf in confs:
                                vals = conf.split("=")
                                if len(vals) != 2:
                                    raise Exception("invalid value " + conf)
                                new_mapping[vals[1]] = vals[0]
                            config["target_devices"][k]["mapping"] = new_mapping
                    ndevices += 1
        # save !
        self.save_config(config_name, config)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="keyboardToPads")
    parser.add_argument("--search", action="store_true")
    parser.add_argument("--config")
    parser.add_argument("--input")
    parser.add_argument("--run",    action="store_true")
    parser.add_argument("--rules",  action="store_true")
    parser.add_argument("--get-config",    action="store_true")

    # set keys
    parser.add_argument("--set", action="store_true", help="edit configuration from command line")
    parser.add_argument("--device-number", type=int)
    parser.add_argument("--device-name",   type=str)
    parser.add_argument("--device-type",   type=str)
    parser.add_argument("--device-keep",   type=int, help="keep only this number of device for the given type")
    parser.add_argument("--set-values",    type=str)

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
        if args.get_config and args.config:
            KeyboardController().get_config(args.config)
        elif args.set:
            KeyboardController().do_set(args.config, args.device_number, args.device_name, args.device_type, args.device_keep, args.set_values)
        else:
            parser.error("with --config, at least one of --run, --get-config, --set and --rules required")
            parser.print_help()
