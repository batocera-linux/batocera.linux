#!/usr/bin/env python
import ConfigParser
import StringIO
import os
import re
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
        try:
            # TODO: remove me when we migrate to Python 3
            # pretend where have a [DEFAULT] section
            file = StringIO.StringIO()
            file.write('[DEFAULT]\n')
            file.write(open(self.settingsFile).read())
            file.seek(0, os.SEEK_SET)

            self.config.readfp(file)
        except IOError, e:
            eslog.debug(str(e))

    def write(self):
        fp = open(self.settingsFile, 'w')
        for (key, value) in self.config.items('DEFAULT'):
            fp.write("{0}{2}={2}{1}\n".format(key, str(value), self.separator))
        fp.close()

    def load(self, name, default=None):
        eslog.debug("Looking for {0} in {1}".format(name, self.settingsFile))
        return self.config.get('DEFAULT', name, default)

    def save(self, name, value):
        eslog.debug("Writing {0} = {1} to {2}".format(name, value, self.settingsFile))
        # TODO: should we call loadAll first?
        # TODO: do we need proper section support? PSP config is an ini file
        self.config.set('DEFAULT', name, str(value))
        # TODO: do we need to call write() on every save()?
        self.write()

    def disable(self, name):
        raise Exception
        # TODO: check if is ok to remove option instead of comment it
        self.config.remove(name)

    def disableAll(self, name):
        eslog.debug("Disabling {0} from {1}".format(name, self.settingsFile))
        for (key, value) in self.config.items('DEFAULT'):
            m = re.match(r"^" + name, key)
            if m:
                self.config.remove_option('DEFAULT', key)

    def remove(self, name):
        raise Exception
        self.config.remove_option('DEFAULT', name)

    def loadAll(self, name):
        eslog.debug("Looking for {0}.* in {1}".format(name, self.settingsFile))
        res = dict()
        for (key, value) in self.config.items('DEFAULT'):
            m = re.match(r"^" + name + "\.(.+)", key)
            if m:
                res[m.group(1)] = value;

        return res
