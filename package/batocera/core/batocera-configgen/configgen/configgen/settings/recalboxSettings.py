#!/usr/bin/env python
import sys
import os
if __name__ == '__main__':
    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import re
import argparse
import configgen.recalboxFiles as recalboxFiles

settingsFile = recalboxFiles.recalboxConf


def load(name, default=None):
    for line in open(settingsFile):
        if name in line:
            m = re.match(r"^" + name + "=(.+)", line)
            if m:
                return m.group(1)
    return default


def save(name, value):
    os.system("sed -i 's|^.*" + name + "=.*|" + name + "=" + value + "|g' " + settingsFile)
    if load(name) is None:
        with open(settingsFile, "a") as settings:
            settings.write("\n{}={}".format(name, value))


def disable(name):
    # settings=`cat "$es_settings" | sed -n "s/.*name=\"${varname}\" value=\"\(.*\)\".*/\1/p"`
    os.system("sed -i \"s|^.*\({}=.*\)|;\\1|g\" {}".format(name,settingsFile))


def loadAll(name):
    res = dict()
    for line in open(settingsFile):
        if name in line:
            m = re.match(r"^" + name + "\.(.+?)=(.+)", line)
            if m:
                res[m.group(1)] = m.group(2);
    return res

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='recalbox-config script')
    parser.add_argument("-command", help="load, save or disable", type=str, required=True)
    parser.add_argument("-key", help="key to load", type=str, required=True)
    parser.add_argument("-value", help="if command = save value to save", type=str, required=False)
    args = parser.parse_args()

    if args.command == "save" :
        save(args.key, args.value)
    if args.command == "load" :
        loaded = load(args.key)
        if loaded is not None:
            sys.stdout.write(loaded)
    if args.command == "disable" :
        disable(args.key)