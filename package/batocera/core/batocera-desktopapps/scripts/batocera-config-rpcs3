#!/bin/bash

# when the program is called from a non X environment, handle the mouse
# maybe an other choice is better

if test -z "${DISPLAY}"
then
    export DISPLAY=:0.0
fi

XDG_CONFIG_HOME=/userdata/system/configs XDG_CACHE_HOME=/userdata/saves QT_QPA_PLATFORM=xcb XDG_RUNTIME_DIR=/userdata /usr/bin/rpcs3 -platform xcb
