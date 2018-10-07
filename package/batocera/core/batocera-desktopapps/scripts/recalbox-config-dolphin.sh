#!/bin/bash

# when the program is called from a non X environment, handle the mouse
# maybe an other choice is better

if test -z "${DISPLAY}"
then
    export DISPLAY=:0.0
    HANDLEMOUSE=1
    matchbox-remote -s # show the mouse
fi

XDG_CONFIG_HOME=/recalbox/share/system/configs XDG_DATA_HOME=/recalbox/share/saves /usr/bin/dolphin-emu-wx

if test "${HANDLEMOUSE}" = "1"
then
    matchbox-remote -h # hide the mouse
fi
