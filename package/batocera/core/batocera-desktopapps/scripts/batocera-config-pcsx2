#!/bin/bash

# when the program is called from a non X environment, handle the mouse
# maybe an other choice is better

if test -z "${DISPLAY}"
then
    export DISPLAY=:0.0
fi

XDG_CONFIG_HOME=/userdata/system/configs LD_LIBRARY_PATH=/usr/pcsx2/lib /usr/pcsx2/bin/pcsx2
