#!/usr/bin/env python

import re
import os
import configgen.recalboxFiles as recalboxFiles
settingsFile = recalboxFiles.esSettings


def load(name, default=None):
    for line in open(settingsFile):
        if name in line:
            m = re.match(r".*value=\"(.+?)\".*", line)
            if m:
                return m.group(1)
    return default


def save(name, value):
    if load(name) is not None:
        os.system(
            "sed -i 's|name=\"" + name + "\" value=\".*\"|name=\"" + name + "\" value=\"" + value + "\"|g' " + settingsFile)
    else:
        type = "string"
        try:
            int(name)
            type = "int"
        except ValueError:
            if name is "true" or name is "false":
                type = "bool"
        with open(settingsFile, "a") as myfile:
            myfile.write('<{} name="{}" value="{}" />\n'.format(type, name, value))

