#!/usr/bin/env python

import configparser
import os
import re
import io
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)
__source__ = os.path.basename(__file__)

class UnixSettings():

    def __init__(self, settingsFile, separator='', defaultComment='#'):
        self.settingsFile = settingsFile
        self.separator = separator
        # unused. left for compatibility with previous implementation
        self.comment = defaultComment

        # use ConfigParser as backend.
        eslog.debug(f"Creating parser for {self.settingsFile}")
        self.config = configparser.ConfigParser(interpolation=None, strict=False) # strict=False to allow to read duplicates set by users
        # To prevent ConfigParser from converting to lower case
        self.config.optionxform = str

        try:
            # TODO: remove me when we migrate to Python 3
            # pretend where have a [DEFAULT] section
            file = io.StringIO()
            file.write('[DEFAULT]\n')
            file.write(open(self.settingsFile, encoding='utf_8_sig').read())
            file.seek(0, os.SEEK_SET)

            self.config.readfp(file)
        except IOError as e:
            eslog.error(str(e))

    def write(self):
        fp = open(self.settingsFile, 'w')
        try:
            for (key, value) in self.config.items('DEFAULT'):
                fp.write("{0}{2}={2}{1}\n".format(key, str(value), self.separator))
        except:
            # PSX Mednafen writes beetle_psx_hw_cpu_freq_scale = "100%(native)"
            # Python 2.7 is EOL and ConfigParser 2.7 takes "%(" as a won't fix error
            # TODO: clean that up when porting to Python 3
            eslog.error("Wrong value detected (after % char maybe?), ignoring.")
        fp.close()

    def save(self, name, value):
        eslog.debug(f"Writing {name} = {value} to {self.settingsFile}")
        # TODO: do we need proper section support? PSP config is an ini file
        self.config.set('DEFAULT', name, str(value))

    def disableAll(self, name):
        eslog.debug(f"Disabling {name} from {self.settingsFile}")
        for (key, value) in self.config.items('DEFAULT'):
            if key[0:len(name)] == name:
                self.config.remove_option('DEFAULT', key)

    def remove(self, name):
        self.config.remove_option('DEFAULT', name)

    @staticmethod
    def protectString(str):
        return re.sub(r'[^A-Za-z0-9-\.]+', '_', str)

    def loadAll(self, name, includeName = False):
        eslog.debug(f"Looking for {name}.* in {self.settingsFile}")
        res = dict()
        for (key, value) in self.config.items('DEFAULT'):
            m = re.match(r"^" + UnixSettings.protectString(name) + r"\.(.+)", UnixSettings.protectString(key))
            if m:
                if includeName:
                    res[name + "." + m.group(1)] = value;
                else:
                    res[m.group(1)] = value;

        return res
