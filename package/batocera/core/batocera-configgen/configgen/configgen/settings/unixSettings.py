#!/usr/bin/env python

import ConfigParser
import StringIO
import os
import re
import io
from configgen.utils.logger import eslog

__source__ = os.path.basename(__file__)

class UnixSettings():

    def __init__(self, settingsFile, separator='', defaultComment='#'):
        self.settingsFile = settingsFile
        self.separator = separator
        # unused. left for compatibility with previous implementation
        self.comment = defaultComment

        # use ConfigParser as backend.
        eslog.debug("Creating parser for {0}".format(self.settingsFile))
        self.config = ConfigParser.ConfigParser()
        # To prevent ConfigParser from converting to lower case
        self.config.optionxform = str

        try:
            # TODO: remove me when we migrate to Python 3
            # pretend where have a [DEFAULT] section
            file = StringIO.StringIO()
            file.write('[DEFAULT]\n')
            file.write(io.open(self.settingsFile, encoding='utf_8_sig').read())
            file.seek(0, os.SEEK_SET)

            self.config.readfp(file)
        except IOError, e:
            eslog.debug(str(e))

    def write(self):
        fp = open(self.settingsFile, 'w')
        try:
            for (key, value) in self.config.items('DEFAULT'):
                fp.write("{0}{2}={2}{1}\n".format(key, str(value), self.separator))
        except:
            # PSX Mednafen writes beetle_psx_hw_cpu_freq_scale = "100%(native)"
            # Python 2.7 is EOL and ConfigParser 2.7 takes "%(" as a won't fix error
            # TODO: clean that up when porting to Python 3
            eslog.debug("Wrong value detected (after % char maybe?), ignoring.")
        fp.close()

    def load(self, name, default=None):
        try:
            eslog.debug("Looking for {0} in {1}".format(name, self.settingsFile))
            return self.config.get('DEFAULT', name, default)
        except ConfigParser.NoOptionError, e:
            return None

    def save(self, name, value):
        eslog.debug("Writing {0} = {1} to {2}".format(name, value, self.settingsFile))
        # TODO: do we need proper section support? PSP config is an ini file
        self.config.set('DEFAULT', name, str(value))

    def disable(self, name):
        # unused?
        raise Exception
        self.config.remove(name)

    def disableAll(self, name):
        eslog.debug("Disabling {0} from {1}".format(name, self.settingsFile))
        for (key, value) in self.config.items('DEFAULT'):
            m = re.match(r"^" + name, key)
            if m:
                self.config.remove_option('DEFAULT', key)

    def remove(self, name):
        self.config.remove_option('DEFAULT', name)

    @staticmethod
    def protectString(str):
        return re.sub('[^A-Za-z0-9-\.]+', '_', str)

    def loadAll(self, name):
        eslog.debug("Looking for {0}.* in {1}".format(name, self.settingsFile))
        res = dict()
        for (key, value) in self.config.items('DEFAULT'):
            m = re.match(r"^" + UnixSettings.protectString(name) + "\.(.+)", UnixSettings.protectString(key))
            if m:
                res[m.group(1)] = value;

        return res
