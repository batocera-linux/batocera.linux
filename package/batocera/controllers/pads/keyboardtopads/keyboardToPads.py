#!/usr/bin/env python3

import yaml
import argparse
import json
import subprocess

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
            cmd.extend(["--output", "name={}".format(target_device["name"])])

            # output filter (remove doubles)
            keyslist = {}
            for mapping, value in target_device["mapping"].items():
                valueParts = value.split(':')
                valuetypename = valueParts[0] + ":" + valueParts[1]
                keyslist[valuetypename] = True
            for mapping in keyslist:
                cmd.append(mapping)
        return cmd

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="keycontroller")
    parser.add_argument("--config", required=True)
    parser.add_argument("--input")
    parser.add_argument("--run",    action="store_true")
    parser.add_argument("--rules",  action="store_true")
    args = parser.parse_args()

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
        parser.print_help()
