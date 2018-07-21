#!/usr/bin/env python

import re
import os
import configgen.recalboxFiles as recalboxFiles
import shutil
settingsFile = recalboxFiles.retroarchCustom
settingsFileOriginal = recalboxFiles.retroarchCustomOrigin


def load(name, default=None):
    for line in open(settingsFile):
        if name in line:
            m = re.match(r"^" + name + " ?= ?\"(.+)\"", line)
            if m:
                return m.group(1)
            else:
                m = re.match(r"^" + name + " ?= ?(.+)", line)
                if m:
                    return m.group(1)
    return default


def save(name, value):
    os.system("sed -i \"s|#\?{} \?=.*|{} = {}|g\" {}".format(name, name, value, settingsFile))
    if load(name) is None:
        with open(settingsFile, "a+") as settings:
            settings.write("{} = {}\n".format(name, value))


def disable(name):
    os.system("sed -i \"s|^.*\({} =.*\)|#\\1|g\" {}".format(name, settingsFile))

def copyFromOriginal():
    shutil.copyfile(settingsFileOriginal, settingsFile)