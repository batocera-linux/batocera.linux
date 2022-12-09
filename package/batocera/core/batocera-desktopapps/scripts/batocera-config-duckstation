#!/bin/bash

# when the program is called from a non X environment, handle the mouse
# maybe an other choice is better

if test -z "${DISPLAY}"
then
    export DISPLAY=:0.0
fi

# We don't have QT library installed on SBC
if [-e /usr/bin/duckstation-qt] ; then
    XDG_CONFIG_HOME=/userdata/system/configs XDG_DATA_HOME=/userdata/saves QT_QPA_PLATFORM=xcb /usr/bin/duckstation-qt
else
    XDG_CONFIG_HOME=/userdata/system/configs XDG_DATA_HOME=/userdata/saves /usr/bin/duckstation-nogui
fi

