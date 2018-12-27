#!/usr/bin/env python

import ConfigParser
import StringIO
import os
import re
import utils.eslog as eslog

__source__ = os.path.basename(__file__)

class UnixSettings():

    def __init__(self, settingsFile, separator='', defaultComment='#'):
        self.settingsFile = settingsFile
        self.separator = separator
        # unused. left for compatibility with previous implementation
        self.comment = defaultComment

        # use ConfigParser as backend.
        eslog.log("{0}: Creating parser for {1}".format(__source__, self.settingsFile))
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
            eslog.log("{0}: {1}".format(__source__, str(e)))


    def load(self, name, default=None):
        eslog.log("{0}: Looking for {1} from {2}".format(__source__, name, self.settingsFile))
        return self.config.get('DEFAULT', name, default)

    def save(self, name, value):
        eslog.log("{0}: Writing {1} = {2} to {3}".format(__source__, name, value, self.settingsFile))
        # TODO: should we call loadAll first?
        # TODO: do we need proper section support? PSP config is an ini file
        self.config.set('DEFAULT', name, str(value))
        fp = open(self.settingsFile, 'w')
        for (key, value) in self.config.items('DEFAULT'):
            fp.write("{0}{2}={2}{1}\n".format(key, str(value), self.separator))
        fp.close()

    def disable(self, name):
        raise Exception
        # TODO: check if is ok to remove option instead of comment it
        self.config.remove(name)

    def disableAll(self, name):
        eslog.log("{0}: Disabling all options from from {1}".format(__source__, self.settingsFile))
        # TODO: check if is ok to remove whole DEFAULT section
        self.config.remove_section('DEFAULT')

    def remove(self, name):
        raise Exception
        self.config.remove_option('DEFAULT', name)

    def loadAll(self, name):
        eslog.log("{0}: Looking for {1}.* from {2}".format(__source__, name, self.settingsFile))
        res = dict()
        for (key, value) in self.config.items('DEFAULT'):
            m = re.match(r"^" + name + "\.(.+?)", key)
            if m:
                res[m.group(1)] = value;

        return res
