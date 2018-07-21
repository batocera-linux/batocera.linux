#!/usr/bin/env python

import re
import os


class UnixSettings():
    def __init__(self, settingsFile, separator='', defaultComment='#'):
        self.settingsFile = settingsFile

        self.separator = separator
        self.comment = defaultComment

    def load(self, name, default=None):
        separ = self.separator
        if separ is not '':
            separ += "?"
        if not os.path.isfile(self.settingsFile):
            return default
        with open(self.settingsFile) as lines:
            for line in open(self.settingsFile):
                if name in line:
                    m = re.match(r"^" + name + separ + "=" + separ + "\"(.+)\"", line)
                    if m:
                        return m.group(1)
                    else:
                        m = re.match(r"^" + name + separ + "=" + separ + "(.+)", line)
                        if m:
                            return m.group(1)
            return default

    def save(self, name, value):
        if os.path.isfile(self.settingsFile):
            os.system(
                "sed -i 's|^{}\?{}{}=.*|{}{}={}{}|g' {}".format(self.comment, name, self.separator, name,
                                                                  self.separator, self.separator,
                                                                  value, self.settingsFile))
        if self.load(name) is None:
            with open(self.settingsFile, "a+") as settings:
                settings.write("\n{}{}={}{}".format(name, self.separator, self.separator, value))

    def disable(self, name):
        os.system(
            "sed -i \"s|^.*\({}{}\?=.*\)|{}\\1|g\" {}".format(name, self.separator, self.comment, self.settingsFile))

    def disableAll(self, name):
        os.system("sed -i \"s|^.*\({}.*\)|{}\\1|g\" {}".format(name, self.comment, self.settingsFile))

    def remove(self, name):
        os.system(
            "sed -i \"\\|^.*\({}{}\?=.*\)|d\" {}".format(name, self.separator, self.settingsFile))

    def loadAll(self, name):
        res = dict()
        with open(self.settingsFile) as lines:
            for line in lines:
                if name in line:
                    m = re.match(r"^" + name + "\.(.+?)=" + self.separator + "\"(.+)\"", line)
                    if m:
                        res[m.group(1)] = m.group(2);
                    else:
                        m = re.match(r"^" + name + "\.(.+?)=" + self.separator + "(.+)", line)
                        if m:
                            res[m.group(1)] = m.group(2);
        return res
