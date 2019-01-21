#!/usr/bin/env python
import sys
# import os
# if __name__ == '__main__':
#     sys.path.append(
#         os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
#
import argparse
import configgen.recalboxFiles as recalboxFiles
from configgen.settings.unixSettings import UnixSettings

settingsFile = recalboxFiles.recalboxConf

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='recalbox-config script')
    parser.add_argument("-command", help="load, save or disable", type=str, required=True)
    parser.add_argument("-key", help="key to load", type=str, required=True)
    parser.add_argument("-value", help="if command = save value to save", type=str, required=False)
    args = parser.parse_args()

    config = UnixSettings(settingsFile)

    if args.command == "save" :
        # TODO: only load is unused internally. UnixSettings.write() removes file comments.
        #       we can provide inplace editing for small changes
        raise "not supported"
        # save(args.key, args.value)
    if args.command == "load" :
        v = config.load(args.key)
        if v is not None:
            sys.stdout.write(v)
    if args.command == "disable":
        # TODO: only load is unused internally. UnixSettings.write() removes file comments.
        #       we can provide inplace editing for small changes
        raise "not supported"
        # disable(args.key)
