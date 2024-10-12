#!/bin/bash

if test -z "${DISPLAY}"
then
    export DISPLAY=$(getLocalXDisplay)
fi

# set the environment variables
XDG_CONFIG_HOME=$CFGDIR \
XDG_CACHE_HOME=/userdata/system/cache \
XDG_DATA_HOME=/userdata/saves \
XDG_DATA_DIRS=/userdata/saves \
# now run the emulator
/usr/bin/vita3k/Vita3K -F
